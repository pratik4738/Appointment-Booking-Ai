# app.py - FastAPI Backend with LangGraph Agent
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
import json
from langgraph.graph import StateGraph, END

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import asyncio
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle
import re
from dateutil import parser
from dateutil.relativedelta import relativedelta

app = FastAPI(title="Calendar Agent API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Calendar setup
SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.service = None
        self.setup_calendar_service()
    
    def setup_calendar_service(self):
        """Setup Google Calendar service"""
        creds = None
        # Load existing credentials
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # For demo purposes, we'll create mock credentials
                # In production, you'd use the OAuth flow
                self.service = self._create_mock_service()
                return
        
        if creds:
            self.service = build('calendar', 'v3', credentials=creds)
        else:
            self.service = self._create_mock_service()
    
    def _create_mock_service(self):
        """Create a mock service for demo purposes"""
        class MockService:
            def __init__(self):
                self.events_data = []
            
            class Events:
                def __init__(self, parent):
                    self.parent = parent
                
                def list(self, calendarId, timeMin, timeMax, singleEvents=True, orderBy='startTime'):
                    # Mock existing events
                    mock_events = {
                        'items': [
                            {
                                'id': 'mock1',
                                'summary': 'Existing Meeting',
                                'start': {'dateTime': '2024-12-30T10:00:00Z'},
                                'end': {'dateTime': '2024-12-30T11:00:00Z'}
                            }
                        ]
                    }
                    
                    class MockExecute:
                        def execute(self):
                            return mock_events
                    
                    return MockExecute()
                
                def insert(self, calendarId, body):
                    self.parent.events_data.append(body)
                    
                    class MockExecute:
                        def execute(self):
                            return {'id': f'mock_{len(self.parent.events_data)}'}
                    
                    return MockExecute()
            
            def events(self):
                return self.Events(self)
        
        return MockService()
    
    def get_free_slots(self, start_date: datetime, end_date: datetime, duration_minutes: int = 60):
        """Get available time slots"""
        try:
            # Query existing events
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Generate potential slots (9 AM to 5 PM, weekdays)
            free_slots = []
            current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
            
            while current < end_date:
                # Skip weekends
                if current.weekday() >= 5:
                    current += timedelta(days=1)
                    continue
                
                # Check if slot conflicts with existing events
                slot_end = current + timedelta(minutes=duration_minutes)
                
                # Skip if outside business hours
                if current.hour < 9 or slot_end.hour > 17:
                    current += timedelta(hours=1)
                    continue
                
                is_free = True
                for event in events:
                    event_start = parser.parse(event['start'].get('dateTime', event['start'].get('date')))
                    event_end = parser.parse(event['end'].get('dateTime', event['end'].get('date')))
                    
                    if (current < event_end and slot_end > event_start):
                        is_free = False
                        break
                
                if is_free:
                    free_slots.append({
                        'start': current.isoformat(),
                        'end': slot_end.isoformat(),
                        'display': current.strftime('%A, %B %d at %I:%M %p')
                    })
                
                current += timedelta(minutes=30)  # Check every 30 minutes
                
                # Limit to 10 slots for demo
                if len(free_slots) >= 10:
                    break
            
            return free_slots
        except Exception as e:
            print(f"Error getting free slots: {e}")
            return []
    
    def book_appointment(self, start_time: datetime, end_time: datetime, title: str, description: str = ""):
        """Book an appointment"""
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            event_result = self.service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return event_result.get('id')
        except Exception as e:
            print(f"Error booking appointment: {e}")
            return None

# Initialize calendar service
calendar_service = CalendarService()

# Tools for the agent
@tool
def check_availability(query: str) -> str:
    """Check calendar availability based on user query"""
    # Parse the query to extract date/time information
    now = datetime.now()
    
    # Simple date parsing logic
    if "tomorrow" in query.lower():
        target_date = now + timedelta(days=1)
    elif "today" in query.lower():
        target_date = now
    elif "next week" in query.lower():
        target_date = now + timedelta(days=7)
    elif "friday" in query.lower():
        days_ahead = 4 - now.weekday()  # Friday is 4
        if days_ahead <= 0:
            days_ahead += 7
        target_date = now + timedelta(days=days_ahead)
    else:
        target_date = now + timedelta(days=1)  # Default to tomorrow
    
    # Set search range
    start_date = target_date.replace(hour=9, minute=0, second=0, microsecond=0)
    end_date = target_date.replace(hour=17, minute=0, second=0, microsecond=0)
    
    # Get free slots
    free_slots = calendar_service.get_free_slots(start_date, end_date)
    
    if not free_slots:
        return "No available slots found for the requested time."
    
    # Format response
    response = f"Available slots for {target_date.strftime('%A, %B %d')}:\n"
    for i, slot in enumerate(free_slots[:5], 1):  # Show top 5 slots
        response += f"{i}. {slot['display']}\n"
    
    return response

@tool
def book_time_slot(slot_info: str, meeting_title: str = "Meeting") -> str:
    """Book a specific time slot"""
    try:
        # Parse the slot info (this is simplified - in production you'd want more robust parsing)
        # For demo, we'll extract datetime from the display string
        now = datetime.now()
        
        # Simple booking logic - in production, you'd parse the exact datetime
        start_time = now + timedelta(days=1, hours=2)  # Mock booking for tomorrow
        end_time = start_time + timedelta(hours=1)
        
        appointment_id = calendar_service.book_appointment(
            start_time=start_time,
            end_time=end_time,
            title=meeting_title,
            description=f"Booked via AI assistant"
        )
        
        if appointment_id:
            return f"✅ Successfully booked: {meeting_title} for {start_time.strftime('%A, %B %d at %I:%M %p')}"
        else:
            return "❌ Failed to book the appointment. Please try again."
    except Exception as e:
        return f"❌ Error booking appointment: {str(e)}"

# Agent State
class AgentState:
    def __init__(self):
        self.messages: List[BaseMessage] = []
        self.user_intent: str = ""
        self.booking_details: Dict[str, Any] = {}
        self.available_slots: List[Dict] = []
        self.pending_confirmation: bool = False

# LangGraph Agent Setup
# LangGraph Agent Setup
class CalendarAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key")
        )
        self.tools = [check_availability, book_time_slot]
        self.tools_map = {tool.name: tool for tool in self.tools}
        self.graph = self._create_graph()

    def run_tool(self, tool_name: str, input_args: dict):
        tool = self.tools_map.get(tool_name)
        if not tool:
            return f"❌ Tool '{tool_name}' not found."
        try:
            return tool.invoke(input_args)
        except Exception as e:
            return f"❌ Tool execution error: {str(e)}"

    def _create_graph(self):
        workflow = StateGraph(dict)

        workflow.add_node("understand_intent", self.understand_intent)
        workflow.add_node("check_calendar", self.check_calendar)
        workflow.add_node("suggest_slots", self.suggest_slots)
        workflow.add_node("confirm_booking", self.confirm_booking)
        workflow.add_node("book_appointment", self.book_appointment)

        workflow.set_entry_point("understand_intent")
        workflow.add_edge("understand_intent", "check_calendar")
        workflow.add_edge("check_calendar", "suggest_slots")
        workflow.add_edge("suggest_slots", "confirm_booking")
        workflow.add_edge("confirm_booking", "book_appointment")
        workflow.add_edge("book_appointment", END)

        return workflow.compile()

    def understand_intent(self, state: Dict) -> Dict:
        user_message = state.get("user_message", "")

        intent_prompt = ChatPromptTemplate.from_template(
            """You are a calendar booking assistant. Analyze the user's message and determine their intent.
            
            User message: {message}
            
            Classify the intent as one of:
            1. book_appointment - User wants to book a new appointment
            2. check_availability - User wants to check available time slots
            3. reschedule - User wants to reschedule an existing appointment
            4. cancel - User wants to cancel an appointment
            5. general_inquiry - General question about scheduling
            
            Also extract any specific time/date preferences mentioned.
            
            Respond in this format:
            Intent: [intent]
            Time preference: [extracted time/date info or "none"]
            Meeting purpose: [purpose if mentioned or "general meeting"]
            """
        )

        try:
            response = self.llm.invoke(intent_prompt.format(message=user_message))
            intent_analysis = response.content

            lines = intent_analysis.strip().split('\n')
            intent = "book_appointment"
            time_pref = "none"
            purpose = "Meeting"

            for line in lines:
                if line.startswith("Intent:"):
                    intent = line.split(":", 1)[1].strip()
                elif line.startswith("Time preference:"):
                    time_pref = line.split(":", 1)[1].strip()
                elif line.startswith("Meeting purpose:"):
                    purpose = line.split(":", 1)[1].strip()

            state.update({
                "intent": intent,
                "time_preference": time_pref,
                "meeting_purpose": purpose
            })

        except Exception:
            state.update({
                "intent": "book_appointment",
                "time_preference": "none",
                "meeting_purpose": "Meeting"
            })

        return state

    def check_calendar(self, state: Dict) -> Dict:
        time_pref = state.get("time_preference", "tomorrow")
        try:
            availability = self.run_tool("check_availability", {"query": time_pref})
            state["availability_response"] = availability
        except Exception:
            state["availability_response"] = "Unable to check calendar availability at the moment."
        return state

    def suggest_slots(self, state: Dict) -> Dict:
        availability = state.get("availability_response", "")

        suggestion_prompt = ChatPromptTemplate.from_template(
            """You are a helpful calendar assistant. Based on the availability information, 
            suggest suitable time slots to the user in a conversational manner.
            
            Availability info: {availability}
            User's time preference: {time_pref}
            
            Provide a friendly response suggesting the available slots and ask the user to choose one.
            Be conversational and helpful.
            """
        )

        try:
            response = self.llm.invoke(suggestion_prompt.format(
                availability=availability,
                time_pref=state.get("time_preference", "")
            ))
            state["suggestion_response"] = response.content
        except Exception:
            state["suggestion_response"] = "I found some available slots. Please let me know which time works best for you."

        return state

    def confirm_booking(self, state: Dict) -> Dict:
        state["confirmation_needed"] = True
        state["confirmation_message"] = "Please confirm if you'd like me to book this appointment."
        return state

    def book_appointment(self, state: Dict) -> Dict:
        meeting_purpose = state.get("meeting_purpose", "Meeting")
        try:
            booking_result = self.run_tool("book_time_slot", {
                "slot_info": "selected_slot",
                "meeting_title": meeting_purpose
            })
            state["booking_result"] = booking_result
        except Exception:
            state["booking_result"] = "❌ Sorry, I couldn't book the appointment. Please try again."
        return state

    async def process_message(self, message: str) -> str:
        try:
            result = self.graph.invoke({
                "user_message": message
            })

            if "suggestion_response" in result:
                return result["suggestion_response"]
            elif "booking_result" in result:
                return result["booking_result"]
            else:
                return "I'm here to help you schedule appointments. What would you like to book?"

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."


# Initialize the agent
calendar_agent = CalendarAgent()

# API Models
class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

# API Endpoints
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint for the calendar agent"""
    try:
        response = await calendar_agent.process_message(chat_message.message)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Calendar Agent API is running"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Calendar Booking Agent API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
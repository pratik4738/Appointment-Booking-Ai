# streamlit_app.py - Streamlit Frontend
import streamlit as st
import requests
import json
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="AI Calendar Assistant",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 0.75rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 2rem;
    }
    
    .bot-message {
        background-color: #e9ecef;
        color: #333;
        padding: 0.75rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 2rem;
    }
    
    .sidebar-info {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .status-indicator {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
    
    .status-connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .status-disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Check if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def send_message_to_agent(message: str):
    """Send message to the calendar agent API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={"message": message},
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "❌ Unable to connect to the calendar service. Please make sure the backend is running."
    except requests.exceptions.Timeout:
        return "⏱️ Request timed out. Please try again."
    except Exception as e:
        return f"❌ An error occurred: {str(e)}"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    
if "api_status" not in st.session_state:
    st.session_state.api_status = check_api_health()

# Sidebar
with st.sidebar:
    st.markdown("## 📅 Calendar Assistant")
    
    # API Status
    api_status = check_api_health()
    if api_status:
        st.markdown('<div class="status-indicator status-connected">🟢 Connected to Calendar Service</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-indicator status-disconnected">🔴 Calendar Service Offline</div>', 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Information panel
    st.markdown("""
    <div class="sidebar-info">
    <h4>💡 How to Use</h4>
    <p>Simply type your scheduling requests in natural language:</p>
    <ul>
        <li>"Schedule a meeting tomorrow at 2 PM"</li>
        <li>"Do you have any free time this Friday?"</li>
        <li>"Book a call between 3-5 PM next week"</li>
        <li>"I need a 30-minute slot tomorrow afternoon"</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Sample prompts
    st.markdown("### 🎯 Quick Actions")
    
    sample_prompts = [
        "Check my availability for tomorrow",
        "Schedule a meeting for Friday afternoon",
        "Book a 1-hour call next week",
        "Show me free slots for today"
    ]
    
    for prompt in sample_prompts:
        if st.button(prompt, key=f"sample_{prompt}", use_container_width=True):
            st.session_state.sample_prompt = prompt
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Current time
    st.markdown(f"**Current Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Main content area
st.markdown('<h1 class="main-header">🤖 AI Calendar Assistant</h1>', unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <p style="font-size: 1.2rem; color: #666;">
        Your intelligent scheduling companion. Book appointments, check availability, and manage your calendar through natural conversation.
    </p>
</div>
""", unsafe_allow_html=True)

# Chat interface
chat_container = st.container()

with chat_container:
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', 
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bot-message">🤖 {message["content"]}</div>', 
                       unsafe_allow_html=True)

# Handle sample prompt selection
if "sample_prompt" in st.session_state:
    user_input = st.session_state.sample_prompt
    del st.session_state.sample_prompt
else:
    user_input = None

# Chat input
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_message = st.text_input(
            "Type your message here...",
            placeholder="e.g., 'Schedule a meeting for tomorrow at 2 PM'",
            value=user_input if user_input else "",
            key="user_input"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send 📤", use_container_width=True)

# Process user input
if submit_button and user_message:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_message})
    
    # Show typing indicator
    with st.spinner("🤖 Thinking..."):
        # Send message to agent
        bot_response = send_message_to_agent(user_message)
    
    # Add bot response to chat
    st.session_state.messages.append({"role": "assistant", "content": bot_response})
    
    # Rerun to display new messages
    st.rerun()

# Welcome message for new users
if not st.session_state.messages:
    st.markdown("""
    <div class="chat-container">
        <div class="bot-message">
            👋 Hello! I'm your AI Calendar Assistant. I can help you:
            <br><br>
            - Check your calendar availability<br>
            - Schedule new appointments<br>
            - Find suitable time slots<br>
            - Book meetings with natural language<br>
            <br>
            Just tell me what you'd like to schedule, and I'll take care of the rest!
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>🚀 Powered by FastAPI, LangGraph, and Streamlit | 
    Built with ❤️ for seamless calendar management</p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh API status every 30 seconds
if st.session_state.get("last_health_check", 0) < time.time() - 30:
    st.session_state.api_status = check_api_health()
    st.session_state.last_health_check = time.time()
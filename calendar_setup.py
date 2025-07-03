import requests
import datetime
from dotenv import load_dotenv
import os

    # Load environment variables from the .env file
load_dotenv()

CRONOFY_TOKEN_URL = "https://api.cronofy.com/oauth/token"
CRONOFY_EVENTS_URL = "https://api.cronofy.com/v1/calendars/{calendar_id}/events"
CRONOFY_CALENDARS_URL = "https://api.cronofy.com/v1/calendars"

def get_access_token():
    data = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("REFRESH_TOKEN")  
    }
    response = requests.post(CRONOFY_TOKEN_URL, data=data)
    if response.ok:
        return response.json()["access_token"]
    else:
        print("Failed to get access token:", response.text)
        return None

def list_calendars():
    token = get_access_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(CRONOFY_CALENDARS_URL, headers=headers)
    if response.ok:
        calendars = response.json().get("calendars", [])
        for cal in calendars:
            print(f"- {cal['calendar_name']} ({cal['calendar_id']})")
        return calendars
    else:
        print("Error fetching calendars:", response.text)

def create_event(calendar_id):
    token = get_access_token()
    if not token:
        return

    headers = {"Authorization": f"Bearer {token}"}
    start = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(hour=14, minute=0, second=0, microsecond=0)
    end = start + datetime.timedelta(hours=1)

    # Convert to ISO 8601 format with Z
    start_str = start.isoformat(timespec='seconds') + "Z"
    end_str = end.isoformat(timespec='seconds') + "Z"

    data = {
        "event_id": "test-ai-calendar-agent",
        "summary": "AI Calendar Test Event",
        "description": "This is a test event using Cronofy.",
        "start": start_str,
        "end": end_str,
        "tzid": "Etc/UTC"
    }

    response = requests.post(CRONOFY_EVENTS_URL.format(calendar_id=calendar_id), headers=headers, json=data)
    if response.ok:
        print("✅ Event created successfully!")
    else:
        print("❌ Failed to create event:", response.text)


if __name__ == '__main__':
    print("🔧 Cronofy Calendar Setup")
    calendars = list_calendars()
    if calendars:
        calendar_id = calendars[0]["calendar_id"]
        create_event(calendar_id)

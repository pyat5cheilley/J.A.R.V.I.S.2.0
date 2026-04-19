"""Calendar handler for J.A.R.V.I.S. 2.0
Manages Google Calendar events: listing, creating, and summarizing upcoming events.
"""

import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = 'DATA/calendar_token.pickle'
CREDENTIALS_PATH = os.getenv('GOOGLE_CREDENTIALS_PATH', 'DATA/credentials.json')


def get_calendar_service():
    """Authenticate and return a Google Calendar service object."""
    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                raiseNotFoundError(
                    f credentials not found at {CREDENTIALS_PATH} "
                    "Please download_client_secrets_file()
            creds = flow.0)

        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)

    return build('calendar', 'v3', credentials=creds)


def get_upcoming_events(max_results: int = 10, days_ahead: int = 7) -> list[dict]:
    """Fetch upcoming calendar events within the specified number of days."""
    try:
        service = get_calendar_service()
        now = datetime.datetime.utcnow()
        end_time = now + datetime.timedelta(days=days_ahead)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return events_result.get('items', [])
    except Exception as e:
        print(f"[CalendarHandler] Error fetching events: {e}")
        return []


def create_event(summary: str, start_time: datetime.datetime,
                 end_time: datetime.datetime, description: str = '',
                 location: str = '') -> dict | None:
    """Create a new calendar event."""
    try:
        service = get_calendar_service()
        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': os.getenv('TIMEZONE', 'UTC'),
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': os.getenv('TIMEZONE', 'UTC'),
            },
        }
        created = service.events().insert(calendarId='primary', body=event).execute()
        print(f"[CalendarHandler] Event created: {created.get('htmlLink')}")
        return created
    except Exception as e:
        print(f"[CalendarHandler] Error creating event: {e}")
        return None


def summarize_events_for_jarvis(events: list[dict]) -> str:
    """Format a list of calendar events into a readable summary for JARVIS responses."""
    if not events:
        return "No upcoming events found."

    lines = ["Here are your upcoming events:"]
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date', 'Unknown time'))
        summary = event.get('summary', 'No title')
        location = event.get('location', '')
        loc_str = f" @ {location}" if location else ''
        # Format ISO datetime to readable
        try:
            dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            start_fmt = dt.strftime('%A, %b %d at %I:%M %p')
        except Exception:
            start_fmt = start
        lines.append(f"  - {summary}{loc_str} — {start_fmt}")

    return '\n'.join(lines)

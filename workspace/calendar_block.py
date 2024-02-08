import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Path to your credentials JSON file
CREDS_PATH = '/Users/sourabhsjain/Documents/projects/python-google-meet/credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.events',
          'https://www.googleapis.com/auth/admin.directory.resource.calendar']


def create_meet_link():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
         token.write(creds.to_json())

    # Load credentials
    # credentials = service_account.Credentials.from_service_account_file(CREDS_PATH, scopes=SCOPES)

    # Build the service
    service = build('calendar', 'v3', credentials=creds)

    # Event details
    event = {
    'summary': 'Google I/O 2015',
    'location': '800 Howard St., San Francisco, CA 94103',
    'description': 'A chance to hear more about Google\'s developer products.',
    'start': {
        'dateTime': '2024-02-01T09:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'end': {
        'dateTime': '2024-02-02T17:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    },
    'recurrence': [
        'RRULE:FREQ=DAILY;COUNT=2'
    ],
    'attendees': [
        {'email': 'xxx@xxx.com'}
    ],
    'reminders': {
        'useDefault': False,
        'overrides': [
        {'method': 'email', 'minutes': 24 * 60},
        {'method': 'popup', 'minutes': 10},
        ],
    },
    'conferenceData': {
        'createRequest': {
            'requestId': 1234,  # A unique request ID 
            'conferenceSolutionKey': {
                'type': 'hangoutsMeet' 
            }
        }
    },
    }

    calendar_id = 'primary'  # Use 'primary' for the user's default calendar

    try:
        event = service.events().insert(calendarId=calendar_id, body=event, conferenceDataVersion=1).execute()
        meet_link = event.get('hangoutLink')
        print(f'Event created: {event.get("htmlLink")}')
        print(f'Google Meet Link: {meet_link}')
    except Exception as e:
        print(f'Error creating event: {e}')


if __name__ == '__main__':
   create_meet_link()

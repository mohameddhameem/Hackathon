#  Copyright (c) 2019. UBS
#  this file contains the logic to retrieve calendar entries from Google
#  for other systems like Outlook / Lotus Notes the API endpoints need to be reconfigured based on the source system

from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarHelper:

    def getPastMeetingDetails(self):
        try:
            #all calendar action here
            creds = None
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)

            # Lets try to create the credential file if not exisits
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server()
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)

            service = build('calendar', 'v3', credentials=creds)

            # Call the Calendar API
            onehour = datetime.datetime.utcnow() - datetime.timedelta(minutes=60)
            #now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            now = onehour.isoformat() + 'Z'  # 'Z' indicates UTC time
            print('Time requested is -> ', )
            ##### NOW LETS TAKE ONLY LAST 1 HR MEETING INVITES.
            #now = now - datetime.timedelta(minutes=60)
            print('Getting the Previous 2 events ->', now)
            events_result = service.events().list(calendarId='primary', timeMin=now,
                                                  maxResults=1, singleEvents=True,
                                                  orderBy='startTime').execute()
            events = events_result.get('items', [])
            #print(events_result)
            if not events:
                print('No upcoming events found.')
            for event in events:
                #start = event['start'].get('dateTime', event['start'].get('date'))
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                print(event)
                print('Organizer ', event['creator'])
                organizer = event['creator']
                print(start, event['summary'])
                title = event['summary']
                attendees = ''
                for attendee in event['attendees']:
                    attendees = attendee.get('email', attendee.get('email')) + "; "

                    print(attendees)
                return start, end, attendees, organizer,title
        except Exception as e:
            raise e

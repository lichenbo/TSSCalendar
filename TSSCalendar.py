# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import httplib2
import os
import sys
import TSS.TSS as TSS

from apiclient import discovery
from oauth2client import file
from oauth2client import client
from oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


# CLIENT_SECRETS is name of a file containing the OAuth 2.0 information for this
# application, including client_id and client_secret. You can see the Client ID
# and Client secret on the APIs page in the Cloud Console:
# <https://cloud.google.com/console#/project/326309019756/apiui>
CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes. PLEASE ONLY ADD THE SCOPES YOU
# NEED. For more information on using scopes please see
# <https://developers.google.com/+/best-practices>.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/calendar',
      'https://www.googleapis.com/auth/calendar.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def main(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('TSSCalendarStorage.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(FLOW, storage, flags)

  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Calendar API.
  service = discovery.build('calendar', 'v3', http=http)

  try:
    print "Ready"
    selectedCalendar = ""
    calendar_list = service.calendarList().list().execute()
    event_list = []
    for calendar in calendar_list['items']:
        if calendar['summary'] == 'TSS' :
            selectedCalendar = calendar
            page_token = None
            while True:
                events = service.events().list(calendarId=calendar['id'], pageToken=page_token).execute()
                event_list.extend(events['items'])
                page_token = events.get('nextPageToken')
                if not page_token:
                    break
            break
    if not selectedCalendar:
        list_entry = {
                  'summary':'TSS',
                  'timeZone':'Asia/Shanghai'
                  }
        selectedCalendar = service.calendars().insert(body=list_entry).execute()


    # Username and password Here
    TSS.login('#TSS USERNAME HERE#','#TSS PASSWORD HERE#')
    print('logged in')


    mycourses = TSS.getMyCourse()
    print('courses gotten')
    for course in mycourses:
        print('course pending ' + course['course_id'])
        for assignment in TSS.getCourseAssignment(course['course_id']):
            print('assignment pending' + assignment['assignment_number'])
            event = {
                     'summary': 'Assignment ' + assignment['assignment_number'] + ' of ' + course['course_name'] + ' reaching its DDL',
                     'start': {
                                'date': assignment['due_date'].split(' ')[0]
                                },
                     'end': {
                             'date': assignment['due_date'].split(' ')[0]
                             },
                     }
            #if event['summary'] in map((lambda e: e['summary']),event_list):
            if event['summary'] in [e['summary'] for e in event_list]:
                print('event exists')
            else:
                print('event creating...' + course['course_name'])
                service.events().insert(calendarId=selectedCalendar['id'], body=event).execute()
                print('event created')

  except client.AccessTokenRefreshError:
    print ("The credentials have been revoked or expired, please re-run"
      "the application to re-authorize")


# For more information on the Calendar API you can visit:
#
#   https://developers.google.com/google-apps/calendar/firstapp
#
# For more information on the Calendar API Python library surface you
# can visit:
#
#   https://developers.google.com/resources/api-libraries/documentation/calendar/v3/python/latest/
#
# For information on the Python Client Library visit:
#
#   https://developers.google.com/api-client-library/python/start/get_started
if __name__ == '__main__':
  main(sys.argv)

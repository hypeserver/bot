from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.write']

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
RANGE_NAME = 'Messages'

class Sheet():
    @classmethod
    def append(cls, row, subsheet=RANGE_NAME):
        values = [row,]
        body = {
            'values': values
        }
        service = build('sheets', 'v4')
        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=subsheet,
            valueInputOption='RAW', body=body).execute()

        print('{0} cells appended.'.format(result \
                                            .get('updates') \
                                            .get('updatedCells')))

if __name__ == '__main__':
    row = ['test', 'test', 'test', 'test']
    Sheet.append(row)

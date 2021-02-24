from __future__ import print_function
import pickle
import os.path
import google.auth
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
]

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")

ENV = os.environ.get("FLASK_ENV", "production")
ENV_SHEET_MAP = {
    "development": "links-dev",
    "production": "links-main",
}
RANGE_NAME = ENV_SHEET_MAP[ENV]

credentials, project = google.auth.load_credentials_from_file('credentials.json', scopes=SCOPES)

class Sheet():
    @classmethod
    def append(cls, row):
        service = build('sheets', 'v4', credentials=credentials)
        values = [row,]
        body = {
            'values': values
        }

        result = service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME,
            valueInputOption='RAW', body=body).execute()

if __name__ == '__main__':
    row = ['test', 'test', 'test', 'test']
    Sheet.append(row)

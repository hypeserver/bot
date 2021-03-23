import os.path

from googleapiclient.discovery import build

import config as cfg

# If modifying these scopes, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.write"]

RANGE_NAME = "Messages"


class Sheet:
    @classmethod
    def append(cls, row, subsheet=RANGE_NAME):
        values = [
            row,
        ]
        body = {"values": values}
        service = build("sheets", "v4")
        result = (
            service.spreadsheets()
            .values()
            .append(spreadsheetId=cfg.SPREADSHEET_ID, range=subsheet, valueInputOption="RAW", body=body)
            .execute()
        )

        print("{} cells appended.".format(result.get("updates").get("updatedCells")))


if __name__ == "__main__":
    row = ["test", "test", "test", "test"]
    Sheet.append(row)

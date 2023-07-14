import gspread
import requests
from pathlib import Path

import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = "Wings (2023-2024)"
INCLUDED_SHEETS = ["Cheat Sheet"]
PATH_TO = "docs/"
PDF_FILENAME = "rw-cheatsheet"
CREDENTIALS = str(Path.home()) + "/secrets/rwcs-credentials.json"


def main():
    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS,
        scopes=SCOPES,
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    client = gspread.authorize(credentials)
    spreadsheet = client.open(SPREADSHEET_NAME)

    sheets = spreadsheet.worksheets()
    excludedSheetIds = []
    for s in sheets:
        if s.title not in INCLUDED_SHEETS:
            excludedSheetIds.append(s.id)

    hideSheets(spreadsheet, excludedSheetIds)

    url = (
        "https://docs.google.com/spreadsheets/export?format=pdf&portrait=false&id="
        + spreadsheet.id
    )
    headers = {
        "Authorization": "Bearer " + access_token,
    }
    response = requests.get(url, headers=headers)
    pdf = open(PATH_TO + PDF_FILENAME + ".pdf", "wb")
    pdf.write(response.content)
    pdf.close

    showSheets(spreadsheet, excludedSheetIds)


def hideSheets(spreadsheet, ids):
    return toggleSheets(spreadsheet, ids, True)


def showSheets(spreadsheet, ids):
    return toggleSheets(spreadsheet, ids, False)


def toggleSheets(spreadsheet, ids, toggle):
    # toggle: True to hide, False to show
    body = {"requests": []}
    for i in ids:
        request = {
            "updateSheetProperties": {
                "properties": {"sheetId": i, "hidden": toggle},
                "fields": "hidden",
            }
        }
        body["requests"].append(request)

    spreadsheet.batch_update(body=body)


main()

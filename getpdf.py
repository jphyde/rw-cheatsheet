import gspread
import requests
import json
from pathlib import Path
from datetime import datetime, timezone

import google.auth
import google.auth.transport.requests
from google.oauth2 import service_account

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = "Red Wings tracker"
INCLUDED_SHEETS = ["Cheat Sheet", "Injured Cheat Sheet"]
EMPTY_CHECK_CELL = "C2"
PATH_TO = "docs/"
PDF_FILENAME = "rw-cheatsheet"
UPD_JSON = "updated.json"
CREDENTIALS = str(Path.home()) + "/secrets/rwcs-credentials.json"
DATE_F = "%Y-%m-%dT%H:%M:%S.%fZ"


def main():
    with open("docs/updated.json") as f:
        data = json.load(f)
    lastModified = datetime.strptime(data["modifiedTime"], DATE_F)

    credentials = service_account.Credentials.from_service_account_file(
        CREDENTIALS,
        scopes=SCOPES,
    )
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)
    access_token = credentials.token

    client = gspread.authorize(credentials)
    spreadsheet = client.open(SPREADSHEET_NAME)

    headers = {
        "Authorization": "Bearer " + access_token,
    }
    modifiedObj = getSheetModifiedTimes(headers, spreadsheet.id)
    modifiedTime = datetime.strptime(modifiedObj["modifiedTime"], DATE_F)
    modifiedByPgmTime = datetime.strptime(modifiedObj["modifiedByMeTime"], DATE_F)

    # only update if last modification was not by this pgm and more recent than stored modify date
    if modifiedTime != modifiedByPgmTime and modifiedTime > lastModified:
        sheets = spreadsheet.worksheets()
        excludedSheetIds = []
        for s in sheets:
            if s.title not in INCLUDED_SHEETS and not isEmpty(s):
                excludedSheetIds.append(s.id)

        if excludedSheetIds:
            hideSheets(spreadsheet, excludedSheetIds)

        url = (
            "https://docs.google.com/spreadsheets/export?format=pdf&portrait=false&id="
            + spreadsheet.id
        )
        response = requests.get(url, headers=headers)
        pdf = open(PATH_TO + PDF_FILENAME + ".pdf", "wb")
        pdf.write(response.content)
        pdf.close

        if excludedSheetIds:
            showSheets(spreadsheet, excludedSheetIds)

        modified_dict = {"modifiedTime": modifiedTime.strftime(DATE_F)}
        json_object = json.dumps(modified_dict)
        print(json_object)
        with open(PATH_TO + UPD_JSON, "w") as outfile:
            outfile.write(json_object)


def getSheetModifiedTime(headers, id):
    url = "https://www.googleapis.com/drive/v3/files/" + id + "?fields=modifiedTime"
    response = requests.get(url, headers=headers)
    res_obj = response.json()
    t = res_obj["modifiedTime"]
    return datetime.strptime(t, DATE_F)


def getSheetModifiedTimes(headers, id):
    url = (
        "https://www.googleapis.com/drive/v3/files/"
        + id
        + "?fields=modifiedTime,modifiedByMeTime"
    )
    response = requests.get(url, headers=headers)
    return response.json()


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


def isEmpty(sheet):
    return sheet.acell(EMPTY_CHECK_CELL) == ""


main()

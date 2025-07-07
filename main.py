from fastapi import FastAPI
import os
import json
import gspread
from io import StringIO
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.openapi.utils import get_openapi

app = FastAPI()

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from env variable
GOOGLE_CREDS_JSON = os.environ["GOOGLE_CREDS_JSON"]
creds_dict = json.loads(GOOGLE_CREDS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SHEET_NAME = "Example"
WORKSHEET_NAME = "Sample"

@app.get("/get_value")
def get_value(key: int):
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    records = sheet.get_all_records()
    for row in records:
        if row["Key"] == key:
            return {"value": row["Value"]}
    return {"value": None, "message": "Key not found"}

@app.get("/openapi.json", include_in_schema=False)
def custom_openapi():
    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {"url": "https://sheets-fastapi.onrender.com"}
    ]
    return openapi_schema


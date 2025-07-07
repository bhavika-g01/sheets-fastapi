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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI",
        version="0.1.0",
        routes=app.routes,
    )
    openapi_schema["servers"] = [
        {
            "url": "https://sheets-fastapi.onrender.com"  # Make sure this matches your actual deployed URL
        }
    ]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# 👇 This is the critical part
app.openapi = custom_openapi

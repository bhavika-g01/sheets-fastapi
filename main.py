from fastapi import FastAPI
import os
import json
import gspread
from io import StringIO
from oauth2client.service_account import ServiceAccountCredentials
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Query

app = FastAPI()

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from env variable
GOOGLE_CREDS_JSON = os.environ["GOOGLE_CREDS_JSON"]
creds_dict = json.loads(GOOGLE_CREDS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

SHEET_NAME = "Example"
WORKSHEET_NAME = "Sample"


@app.get("/shipping_info")
def get_shipping_info(
    sku: str = Query(..., description="SKU like 'wrb-rg-luna-6-rg'")
):
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)
    data = sheet.get_all_records()
    
    for row in data:
        if row["SKUs"] == sku:
            return {
                "sku": row["SKUs"],
                "size": row["Unnamed: 0"],
                "color": row["Colour"],
                "can_ship_tomorrow": row.get("Can be shipped tomorrow", 0),
                "can_ship_in_2_days": row.get("Can be shipped in 2 days", 0),
                "can_ship_in_4_days": row.get("Can be shipped in 4 days", 0)
            }
    
    return {"error": f"No row found with SKU {sku}"}

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

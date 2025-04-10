import os
import json
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

def get_client():
    credentials_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    return gspread.authorize(creds)

def append_to_sheet(sheet_name, row_data):
    try:
        client = get_client()
        sheet = client.open("AniAI Logs").worksheet(sheet_name)
        sheet.append_row(row_data)
    except Exception as e:
        print(f"Ошибка при записи в Google Sheets ({sheet_name}):", e)

def log_feedback(user_full_name, user_id, text):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("Feedback", [user_full_name, str(user_id), text, now])

def log_subscriber(user_id, full_name, username):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("Subscribers", [str(user_id), full_name, username or "", now])

def log_gpt(user_id, full_name, question, answer, lang="auto"):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("GPT", [str(user_id), full_name, question, answer, lang, now])
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

def log_gpt(user_id, full_name, question, answer, lang="auto", session_id=None, history=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    row = [
        str(user_id),
        full_name,
        question,
        answer,
        lang,
        now,
        session_id or "",
        json.dumps(history, ensure_ascii=False) if history else ""
    ]
    append_to_sheet("GPT", row)

def log_translation(user_id, full_name, source_text, translation):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("Translations", [str(user_id), full_name, source_text, translation, now])
    
def log_document_analysis(user_id, full_name, file_name, result):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("Analyze", [str(user_id), full_name, file_name, result, now])

def log_voa_word(user_id, full_name, word):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("VOA Words", [str(user_id), full_name, word, now])

def log_voa_memory(user_id, word, success: bool):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    append_to_sheet("VOA Memory", [str(user_id), word, "✔️" if success else "❌", now])

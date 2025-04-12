import os
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
import fitz  # PyMuPDF
import docx

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Чтение PDF
def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Чтение DOCX
def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Чтение TXT
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.document:
        await update.message.reply_text("📎 Пожалуйста, прикрепи документ (PDF, DOCX или TXT).")
        return

    file = update.message.document
    file_name = file.file_name
    file_ext = os.path.splitext(file_name)[-1].lower()

    if file_ext not in [".pdf", ".docx", ".txt"]:
        await update.message.reply_text("❌ Поддерживаются только PDF, DOCX и TXT.")
        return

    new_file = await file.get_file()
    file_path = f"/tmp/{file.file_unique_id}{file_ext}"
    await new_file.download_to_drive(file_path)

    try:
        if file_ext == ".pdf":
            text = read_pdf(file_path)
        elif file_ext == ".docx":
            text = read_docx(file_path)
        else:
            text = read_txt(file_path)
    except Exception as e:
        await update.message.reply_text(f"Ошибка чтения файла: {e}")
        return

    prompt = update.message.caption or "Выдели главные идеи и сделай краткое резюме:"
    content = text[:3000]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощник, анализирующий документы."},
                {"role": "user", "content": f"{prompt}\n{content}"}
            ]
        )
        result = response.choices[0].message.content
        await update.message.reply_text(f"📊 Результат анализа:\n{result}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка OpenAI: {e}")


import os
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
import fitz  # PyMuPDF
import docx
from handlers.state import active_analyzers
from utils.google_sheets import log_document_analysis

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📄 Чтение PDF
def read_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# 📄 Чтение DOCX
def read_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# 📄 Чтение TXT
def read_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# 🧠 Обработка анализа документа
async def analyze(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_analyzers.add(user_id)

    if not update.message.document:
        await update.message.reply_text("📎 Пожалуйста, прикрепи документ (PDF, DOCX или TXT).")
        return

    file = update.message.document
    file_name = file.file_name
    file_ext = os.path.splitext(file_name)[-1].lower()

    if file_ext not in [".pdf", ".docx", ".txt"]:
        await update.message.reply_text("❌ Поддерживаются только PDF, DOCX и TXT.")
        return

    try:
        tg_file = await file.get_file()
        file_path = f"/tmp/{file.file_unique_id}{file_ext}"
        await tg_file.download_to_drive(file_path)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Не удалось загрузить файл: {e}")
        return

    await update.message.reply_text("⏳ Анализирую документ...")

    try:
        if file_ext == ".pdf":
            text = read_pdf(file_path)
        elif file_ext == ".docx":
            text = read_docx(file_path)
        else:
            text = read_txt(file_path)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при чтении файла: {e}")
        return

    if not text.strip():
        await update.message.reply_text("⚠️ Не удалось извлечь текст из документа.")
        return

    if len(text) > 3000:
        await update.message.reply_text("⚠️ Документ слишком большой. Пожалуйста, сократи его до 3000 символов.")
        return

    prompt = update.message.caption or "Сделай краткое содержание и выдели ключевые идеи:"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты помощница, анализирующая документы и составляющая краткие выводы."},
                {"role": "user", "content": f"{prompt}\n{text}"}
            ]
        )
        result = response.choices[0].message.content.strip()
        await update.message.reply_text(f"📊 Результат анализа:\n{result}")

        log_document_analysis(
            user_id=user_id,
            full_name=update.effective_user.full_name,
            file_name=file.file_name,
            result=result
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при анализе: {e}")

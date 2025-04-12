import os
from openai import OpenAI
from langdetect import detect
from telegram import Update
from telegram.ext import ContextTypes
from utils.google_sheets import log_translate

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args)

    if not text:
        await update.message.reply_text("📤 Пожалуйста, добавь текст после команды /translate.")
        return

    if len(text) > 3000:
        await update.message.reply_text("⚠️ Слишком длинный текст. Пожалуйста, отправь не более 3000 символов.")
        return

    source_lang = detect(text)

    if source_lang == "ru":
        prompt = f"Переведи на английский язык:
{text}"
    else:
        prompt = f"Переведи на русский язык:
{text}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response.choices[0].message.content
        await update.message.reply_text(f"📄 Перевод:
{result}")
        log_translate(user.id, user.full_name, user.username, text)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при переводе:
{e}")



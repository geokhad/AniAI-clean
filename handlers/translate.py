from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("/translate", "").strip()

    if not text:
        await update.message.reply_text("❗ Пожалуйста, укажи текст после команды /translate.")
        return

    if len(text) > 3000:
        await update.message.reply_text("✂️ Слишком много символов. Отправь до 3000 символов за раз.")
        return

    prompt = f"Переведи этот текст на английский или с английского на русский, в зависимости от исходного языка:\n{text}"

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        translation = response.choices[0].message.content
        await update.message.reply_text(translation)
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка: {e}")

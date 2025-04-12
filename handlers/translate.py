from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Активные пользователи, ожидающие перевода
active_translators = set()

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_translators.add(user_id)
    await update.message.reply_text(
        "🌐 Введи текст для перевода.\n"
        "AniAI автоматически определит язык и сделает перевод на русский или английский."
    )

async def handle_translation_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверяем, активировал ли пользователь перевод
    if user_id not in active_translators:
        return

    text = update.message.text.strip()

    if len(text) > 3000:
        await update.message.reply_text("✂️ Слишком много символов. Пожалуйста, отправь до 3000 символов.")
        return

    prompt = (
        "Переведи следующий текст с английского на русский или с русского на английский, "
        "в зависимости от исходного языка:\n\n" + text
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        translation = response.choices[0].message.content
        await update.message.reply_text(translation)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при переводе:\n{e}")
    finally:
        active_translators.discard(user_id)

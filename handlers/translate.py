from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_translators  # 🟢 Состояние
from utils.google_sheets import log_translation  # ✅ Логирование переводов

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_translators.add(user_id)
    await update.message.reply_text(
        "🌐 Введи текст для перевода.\n"
        "AniAI будет автоматически переводить каждый введённый текст.\n\n"
        "📋 Чтобы выйти из режима перевода — нажми кнопку ниже или напиши /menu.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Главное меню", callback_data="go_menu")]
        ])
    )

async def handle_translation_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in active_translators:
        return

    text = update.message.text.strip()

    if not text:
        await update.message.reply_text("❗ Пожалуйста, введи текст для перевода.")
        return

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

        # ✅ Логирование перевода
        log_translation(
            user_id=user_id,
            full_name=update.effective_user.full_name,
            source_text=text,
            translation=translation
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при переводе:\n{e}")

    # ⚠️ Не сбрасываем active_translators — режим остаётся активным

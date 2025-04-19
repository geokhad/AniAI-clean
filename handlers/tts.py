# handlers/tts.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from openai import OpenAI
import os

from handlers.state import active_tts

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎧 Озвучка американским голосом (TTS)
async def tts_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_tts.add(user_id)
    await update.message.reply_text(
        "🔊 Введи текст, и я озвучу его естественным голосом с американским акцентом.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📋 Главное меню", callback_data="go_menu")]
        ])
    )

async def handle_tts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_tts:
        return

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("❗ Пожалуйста, введи текст для озвучивания.")
        return

    await update.message.reply_text("🎧 Генерирую голос...")

    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="onyx",  # "nova" или "onyx" звучат более натуралистично
            input=text
        )
        path = f"/tmp/tts-{user_id}.ogg"
        with open(path, "wb") as f:
            f.write(response.content)

        with open(path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file, caption="🔊 Повторить")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при озвучке: {e}")

    # ❌ Выход из режима после одного воспроизведения
    active_tts.discard(user_id)


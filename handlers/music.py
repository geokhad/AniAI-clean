
import os
import requests
from telegram import Update
from telegram.ext import ContextTypes

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
API_URL = "https://api-inference.huggingface.co/models/suno/bark"

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

# 🎼 Генерация музыки по описанию
async def handle_music_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.callback_query.message
    await message.reply_text("🎧 Генерирую музыку по твоему описанию...")

    prompt = message.text.strip() if message.text else ""
    if not prompt:
        await message.reply_text("❗ Пожалуйста, напиши, какую музыку ты хочешь.")
        return

    try:
        payload = {
            "inputs": prompt
        }
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)

        if response.status_code != 200:
            await message.reply_text(f"⚠️ Ошибка генерации музыки: {response.status_code} — {response.text}")
            return

        audio_path = f"/tmp/music-{update.effective_user.id}.wav"
        with open(audio_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)

        # Отправляем как голосовое сообщение
        with open(audio_path, "rb") as audio_file:
            await message.reply_voice(voice=audio_file, caption="🎶 Вот твоя музыка!")

    except Exception as e:
        await message.reply_text(f"⚠️ Ошибка при генерации музыки: {e}")

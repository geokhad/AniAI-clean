
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
    await update.message.reply_text("🎧 Генерирую музыку по твоему описанию...")

    prompt = update.message.text.strip()
    if not prompt:
        await update.message.reply_text("❗ Пожалуйста, напиши, какую музыку ты хочешь.")
        return

    try:
        payload = {
            "inputs": prompt
        }
        response = requests.post(API_URL, headers=headers, json=payload, stream=True)

        if response.status_code != 200:
            await update.message.reply_text(f"⚠️ Ошибка генерации музыки: {response.status_code} — {response.text}")
            return

        audio_path = f"/tmp/music-{update.effective_user.id}.wav"
        with open(audio_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=4096):
                f.write(chunk)

        # Отправляем как голосовое сообщение
        with open(audio_path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file, caption="🎶 Вот твоя музыка!")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при генерации музыки: {e}")


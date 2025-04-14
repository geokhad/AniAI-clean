import os
import subprocess
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from handlers.state import (
    clear_user_state,
    active_tts,
    active_translators,
    active_imagers,
    active_ask,
    notified_voice_users
)
from utils.google_sheets import log_translation  # ✅ если используется лог

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎙 Обработка голосового ввода
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    voice = update.message.voice

    if not voice:
        await update.message.reply_text("❗ Пожалуйста, отправь голосовое сообщение.")
        return

    await update.message.reply_text("⏳ Распознаю речь...")

    file = await context.bot.get_file(voice.file_id)
    ogg_path = f"/tmp/{voice.file_unique_id}.ogg"
    wav_path = ogg_path.replace(".ogg", ".wav")
    await file.download_to_drive(ogg_path)

    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка ffmpeg: {e}")
        return

    try:
        with open(wav_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        text = transcript.strip()
        await update.message.reply_text(f"📝 Распознано:\n{text}")

        # 💡 Подсказка голосовых команд (однократно)
        if user_id not in notified_voice_users:
            notified_voice_users.add(user_id)
            await update.message.reply_text(
                "💡 Ты можешь просто говорить команды:\n"
                "• «Переведи на русский язык I love you»\n"
                "• «Сгенерируй картинку»\n"
                "• «Озвучь текст»\n"
                "• «Объясни что такое...»\n\n"
                "Я сам включу нужный режим 🤖"
            )

        lower = text.lower()

        # ✅ Быстрый перевод с распознаванием языка
        if "переведи на русский язык" in lower:
            prompt = text.split("переведи на русский язык", 1)[-1].strip()
            await translate_and_reply(update, prompt, "на русский")
            return

        if "переведи на английский язык" in lower:
            prompt = text.split("переведи на английский язык", 1)[-1].strip()
            await translate_and_reply(update, prompt, "на английский")
            return

        # ✅ Распознавание голосовых команд
        if "переведи" in lower or "перевести" in lower:
            clear_user_state(user_id)
            active_translators.add(user_id)
            await update.message.reply_text("🌍 Включён режим перевода. Введи текст.")
            return

        elif "картинку" in lower or "изображение" in lower or "сгенерируй" in lower:
            clear_user_state(user_id)
            active_imagers.add(user_id)
            await update.message.reply_text("📸 Включён режим генерации. Опиши изображение.")
            return

        elif "озвучь" in lower or "прочитай" in lower:
            clear_user_state(user_id)
            active_tts.add(user_id)
            await update.message.reply_text("🗣 Включён режим озвучки. Введи текст.")
            return

        elif "вопрос" in lower or "объясни" in lower or "что такое" in lower:
            clear_user_state(user_id)
            active_ask.add(user_id)
            await update.message.reply_text("🧠 Включён режим GPT. Задай свой вопрос.")
            return

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# 🌍 Переводчик на русский или английский
async def translate_and_reply(update: Update, text: str,

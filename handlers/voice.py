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
from utils.google_sheets import log_translation  # если используется логирование

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

        elif any(word in lower for word in ["картинку", "изображение", "сгенерируй"]):
            clear_user_state(user_id)
            active_imagers.add(user_id)
            await update.message.reply_text("📸 Включён режим генерации. Опиши изображение.")
            return

        elif any(word in lower for word in ["озвучь", "прочитай"]):
            clear_user_state(user_id)
            active_tts.add(user_id)
            await update.message.reply_text("🗣 Включён режим озвучки. Введи текст.")
            return

        elif any(word in lower for word in ["вопрос", "объясни", "что такое"]):
            clear_user_state(user_id)
            active_ask.add(user_id)
            await update.message.reply_text("🧠 Включён режим GPT. Задай свой вопрос.")
            return

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# 🌍 Функция перевода с направлениями
async def translate_and_reply(update: Update, text: str, direction: str):
    try:
        system = (
            "Переведи текст с английского на русский." if direction == "на русский"
            else "Переведи текст с русского на английский."
        )
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ]
        )
        translation = response.choices[0].message.content.strip()
        await update.message.reply_text(f"🌍 Перевод:\n{translation}")
        log_translation(update.effective_user.id, text, translation)  # если логируем
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка перевода: {e}")

# 📢 /tts
async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("🔊 Введите текст после команды /tts.")
        return
    await handle_tts_playback(update, text)

# 📢 Озвучка через кнопку
async def handle_tts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_tts:
        return
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ Пожалуйста, отправьте текст.")
        return
    await handle_tts_playback(update, text)
    active_tts.discard(user_id)

# 🔊 Озвучка текста
async def handle_tts_playback(update: Update, text: str):
    await update.message.reply_text("🎧 Генерирую голосовое сообщение...")
    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=text
        )
        path = f"/tmp/tts-{update.effective_user.id}.ogg"
        with open(path, "wb") as f:
            f.write(response.content)
        with open(path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file, caption="🗣 Озвучка готова!")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка TTS: {e}")

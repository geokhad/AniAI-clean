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
    active_ask
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎙 Распознавание голосовых сообщений (Whisper API)
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
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка конвертации через ffmpeg: {e}")
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

        # ✅ Распознавание голосовых команд
        lower = text.lower()

        if "переведи" in lower or "перевести" in lower:
            clear_user_state(user_id)
            active_translators.add(user_id)
            await update.message.reply_text("🌍 Включён режим перевода. Введи текст для перевода.")
            return

        elif "картинку" in lower or "изображение" in lower or "сгенерируй" in lower:
            clear_user_state(user_id)
            active_imagers.add(user_id)
            await update.message.reply_text("📸 Включён режим генерации. Опиши, что нужно изобразить.")
            return

        elif "озвучь" in lower or "прочитай" in lower:
            clear_user_state(user_id)
            active_tts.add(user_id)
            await update.message.reply_text("🗣 Включён режим озвучки. Введи текст для преобразования в голос.")
            return

        elif "вопрос" in lower or "объясни" in lower or "что такое" in lower:
            clear_user_state(user_id)
            active_ask.add(user_id)
            await update.message.reply_text("🧠 Включён режим GPT-помощи. Задай свой вопрос.")
            return

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# 📢 Озвучка текста через команду /tts
async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("🔊 Введите текст после команды /tts, чтобы озвучить.")
        return
    await handle_tts_playback(update, text)

# 📢 Озвучка текста через режим (по кнопке)
async def handle_tts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_tts:
        return

    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ Пожалуйста, отправьте текст для озвучивания.")
        return

    await handle_tts_playback(update, text)
    active_tts.discard(user_id)

# 🔊 Универсальная функция воспроизведения
async def handle_tts_playback(update: Update, text: str):
    await update.message.reply_text("🎧 Генерирую голосовое сообщение...")

    try:
        response = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            input=text
        )
        ogg_path = f"/tmp/tts-{update.effective_user.id}.ogg"
        with open(ogg_path, "wb") as f:
            f.write(response.content)

        with open(ogg_path, "rb") as audio_file:
            await update.message.reply_voice(voice=audio_file, caption="🗣 Озвучка готова!")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка TTS: {e}")

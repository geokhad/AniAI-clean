import os
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from handlers.state import clear_user_state
from pydub import AudioSegment

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎙 Распознавание голосовых сообщений (Whisper API)
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
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
        AudioSegment.from_file(ogg_path).export(wav_path, format="wav")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка конвертации файла: {e}")
        return

    try:
        with open(wav_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        await update.message.reply_text(f"📝 Распознано:\n{transcript}")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# 📢 Озвучка текста через OpenAI TTS-1-HD
async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("🔊 Введите текст после команды /tts, чтобы озвучить.")
        return

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


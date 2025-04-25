import os
import subprocess
from openai import OpenAI
from telegram import Update
from telegram.ext import ContextTypes

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🎙 Распознавание речи из голосового сообщения
async def recognize_speech_from_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    voice = update.message.voice
    if not voice:
        return ""

    file = await context.bot.get_file(voice.file_id)
    ogg_path = f"/tmp/{voice.file_unique_id}.ogg"
    wav_path = ogg_path.replace(".ogg", ".wav")
    await file.download_to_drive(ogg_path)

    subprocess.run(
        ["ffmpeg", "-y", "-i", ogg_path, "-ar", "16000", "-ac", "1", wav_path],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    with open(wav_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    return transcript.strip()

# 🔈 Генерация озвучки текста
async def speak_text(text: str, user_id: int) -> str:
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text
    )
    path = f"/tmp/tts-{user_id}.ogg"
    with open(path, "wb") as f:
        f.write(response.content)
    return path


import os
import uuid
from pydub import AudioSegment
import speech_recognition as sr
import openai
import aiohttp

recognizer = sr.Recognizer()

async def recognize_speech_from_voice(update, context):
    user_id = update.effective_user.id
    file = await context.bot.get_file(update.message.voice.file_id)

    ogg_path = f"/tmp/{user_id}_{uuid.uuid4()}.ogg"
    wav_path = ogg_path.replace(".ogg", ".wav")

    await file.download_to_drive(ogg_path)

    try:
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                print("Voice recognition complete: ❗ Could not understand audio.")
                return None
            except sr.RequestError as e:
                print(f"Voice recognition error: {e}")
                return None

        print("Voice recognition complete:", text)
        return text

    finally:
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)


async def synthesize_and_send(text: str, chat_id: int, context):
    """Озвучить фразу через OpenAI TTS и отправить в Telegram."""
    filename = f"/tmp/tts_{uuid.uuid4()}.mp3"

    try:
        response = await openai.audio.speech.acreate(
            model="tts-1",
            voice="nova",  # или alloy, echo, fable, onyx, shimmer
            input=text
        )

        with open(filename, "wb") as f:
            f.write(await response.read())

        with open(filename, "rb") as f:
            await context.bot.send_voice(chat_id=chat_id, voice=f)

    except Exception as e:
        print("❌ Ошибка озвучки:", e)

    finally:
        if os.path.exists(filename):
            os.remove(filename)

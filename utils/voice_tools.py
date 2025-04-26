import os
import uuid
from pydub import AudioSegment
import speech_recognition as sr

recognizer = sr.Recognizer()

async def recognize_speech_from_voice(update, context):
    user_id = update.effective_user.id
    file = await context.bot.get_file(update.message.voice.file_id)

    # Уникальные имена файлов
    ogg_path = f"/tmp/{user_id}_{uuid.uuid4()}.ogg"
    wav_path = ogg_path.replace(".ogg", ".wav")

    await file.download_to_drive(ogg_path)

    try:
        # Конвертация ogg в wav
        audio = AudioSegment.from_ogg(ogg_path)
        audio.export(wav_path, format="wav")

        # Распознавание речи
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
        # Удаление временных файлов в любом случае
        if os.path.exists(ogg_path):
            os.remove(ogg_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

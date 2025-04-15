import os
import subprocess
import re
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
from utils.google_sheets import log_translation, log_gpt
from utils.memory import get_session_messages, add_session_message

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

        lower = text.lower()

        if "перевести на русский" in lower or "переведи на русский" in lower:
            prompt = text.split("на русский", 1)[-1].strip()
            await translate_and_reply(update, prompt, "на русский")
            return

        if "перевести на английский" in lower or "переведи на английский" in lower:
            prompt = text.split("на английский", 1)[-1].strip()
            await translate_and_reply(update, prompt, "на английский")
            return

        if any(word in lower for word in ["переведи", "перевести"]):
            clear_user_state(user_id)
            active_translators.add(user_id)
            await update.message.reply_text("🌍 Включён режим перевода. Введи текст.")
            return

        if any(word in lower for word in ["озвучь", "прочитай"]):
            phrase = text.split("озвучь", 1)[-1].strip() if "озвучь" in lower else text.split("прочитай", 1)[-1].strip()
            if phrase:
                await handle_tts_playback(update, phrase)
            else:
                clear_user_state(user_id)
                active_tts.add(user_id)
                await update.message.reply_text("🗣 Включён режим озвучки. Введи текст.")
            return

        if any(word in lower for word in ["картинку", "изображение", "сгенерируй", "изобрази", "создай"]):
            clear_user_state(user_id)
            active_imagers.add(user_id)
            await update.message.reply_text("🤖 Думаю над изображением...")
            from handlers.image import create_image
            await create_image(update, text)
            return

        if any(re.search(pattern, lower) for pattern in [r"кто такой", r"что такое", r"зачем", r"почему", r"как ", r"где ", r"можно ли"]):
            clear_user_state(user_id)
            active_ask.add(user_id)
            await update.message.reply_text("🧠 Думаю над ответом...")

            previous_messages = get_session_messages(user_id)
            previous_messages.append({"role": "user", "content": text})
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=previous_messages
            )
            answer = response.choices[0].message.content.strip()
            await update.message.reply_text("🎤 Озвучка ответа...")
            from handlers.voice import handle_tts_playback
            await handle_tts_playback(update, answer)

            log_gpt(user_id, user.full_name, text, answer)
            add_session_message(user_id, "user", text)
            add_session_message(user_id, "assistant", answer)
            return

        # Если не распознано — предложить выбрать режим
        await update.message.reply_text("🔄 Я не понял команду. Пожалуйста, попробуй ещё раз.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")


# 🌍 Перевод
async def translate_and_reply(update: Update, text: str, direction: str):
    try:
        system = "Переведи текст с английского на русский." if direction == "на русский" else "Переведи текст с русского на английский."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": text}
            ]
        )
        translation = response.choices[0].message.content.strip()
        await update.message.reply_text(f"🌍 Перевод:\n{translation}")
        log_translation(update.effective_user.id, update.effective_user.full_name, text, translation)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка перевода: {e}")

# 🔊 Универсальная озвучка
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

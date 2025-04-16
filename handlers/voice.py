import os
import subprocess
from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from handlers.state import (
    clear_user_state, active_tts, active_translators,
    active_imagers, active_ask, notified_voice_users
)
from utils.memory import get_memory, update_memory
from utils.google_sheets import log_translation
from handlers.image import handle_image_prompt

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

        if not transcript:
            await update.message.reply_text("⚠️ Не удалось распознать речь. Попробуй снова.")
            return

        text = transcript.strip() if isinstance(transcript, str) else str(transcript).strip()

        if not text:
            await update.message.reply_text("⚠️ Речь не распознана. Попробуй ещё раз.")
            return

        await update.message.reply_text(f"📝 Распознано:\n{text}")
        lower = text.lower()

        if user_id not in notified_voice_users:
            notified_voice_users.add(user_id)
            await update.message.reply_text(
                "💡 Ты можешь говорить фразы:\n"
                "• «переведи на русский I love you»\n"
                "• «создай картинку»\n"
                "• «объясни, что такое…»\n"
                "• «озвучь»\n\n"
                "Я сам пойму, что ты хочешь 🤖"
            )

        if "переведи на русский" in lower:
            await translate_and_reply(update, text.split("на русский", 1)[-1].strip(), "на русский")
        elif "переведи на английский" in lower:
            await translate_and_reply(update, text.split("на английский", 1)[-1].strip(), "на английский")
        elif any(word in lower for word in ["переведи", "перевести"]):
            clear_user_state(user_id)
            active_translators.add(user_id)
            await update.message.reply_text("🌍 Включён режим перевода. Введи текст.")
        elif any(word in lower for word in ["озвучь", "прочитай"]):
            phrase = text.split("озвучь", 1)[-1].strip() if "озвучь" in lower else text.split("прочитай", 1)[-1].strip()
            if phrase:
                await handle_tts_playback(update, phrase)
            else:
                clear_user_state(user_id)
                active_tts.add(user_id)
                await update.message.reply_text("🗣 Включён режим озвучки. Введи текст.")
        elif any(word in lower for word in ["картинку", "изображение", "сгенерируй", "создай", "нарисуй"]):
            clear_user_state(user_id)
            active_imagers.add(user_id)
            await update.message.reply_text("🤖 Думаю над изображением...")
            await handle_image_prompt(update, context)
        elif "?" in text or any(word in lower for word in ["объясни", "что такое", "зачем", "как", "почему"]):
            clear_user_state(user_id)
            active_ask.add(user_id)
            await gpt_answer(update, text)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# Остальные функции (translate_and_reply, gpt_answer, handle_tts_playback и др.)
# остаются без изменений. Если нужно — пришлю их тоже.

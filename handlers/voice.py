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
    notified_voice_users,
)
from handlers.exam_mode import active_voa_exam, handle_voa_text_exam
from utils.memory import get_memory, update_memory
from utils.google_sheets import log_translation
from handlers.image import handle_image_prompt
from handlers.music import handle_music_prompt
from utils.safety import contains_prohibited_content

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

        with open(wav_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )

        text = transcript.strip() if transcript else ""

        if not text:
            await update.message.reply_text("⚠️ Не удалось распознать речь. Попробуйте ещё раз.")
            return

        if contains_prohibited_content(text):
            await update.message.reply_text("🚫 Обнаружен недопустимый или опасный запрос. Попробуй переформулировать.")
            return

        lower = text.lower()

        # ✅ Если пользователь находится в режиме VOA Exam
        if user_id in active_voa_exam:
            # Имитация текстового ответа
            update.effective_message.text = text
            await handle_voa_text_exam(update, context)
            return

        # 📝 Обычная обработка голосовых команд
        await update.message.reply_text(f"📝 Распознано:\n{text}")

        if user_id not in notified_voice_users:
            notified_voice_users.add(user_id)
            await update.message.reply_text(
                "💡 Ты можешь говорить команды:\n"
                "• «переведи на русский I love you»\n"
                "• «создай картинку»\n"
                "• «сыграй музыку»\n"
                "• «объясни, что такое…»\n"
                "• «озвучь текст»\n\n"
                "Я сам пойму, что ты хочешь 🤖"
            )

        if "переведи на русский" in lower:
            prompt = text.split("на русский", 1)[-1].strip()
            await translate_and_reply(update, prompt, "на русский")
            return

        if "переведи на английский" in lower:
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

        if any(word in lower for word in ["сыграй", "музыку", "мелодию", "хочу музыку"]):
            await update.message.reply_text("🎧 Думаю над музыкой...")
            await handle_music_prompt(update, context)
            return

        if any(word in lower for word in ["картинку", "изображение", "сгенерируй", "создай", "нарисуй", "изобрази"]):
            clear_user_state(user_id)
            await update.message.reply_text("🤖 Думаю над изображением...")
            await handle_image_prompt(update, context, prompt=text)
            return

        if "?" in text or any(word in lower for word in ["объясни", "что такое", "зачем", "как", "почему"]):
            clear_user_state(user_id)
            active_ask.add(user_id)
            await gpt_answer(update, text)
            return

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

# 🤖 Ответ с GPT
async def gpt_answer(update: Update, prompt: str):
    user_id = update.effective_user.id
    history = get_memory(user_id)

    messages = [{"role": "system", "content": "Ты полезный помощник в Telegram."}]
    for q, a in history:
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
    messages.append({"role": "user", "content": prompt})

    await update.message.reply_text("🤔 Думаю над ответом...")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        answer = response.choices[0].message.content.strip()
        await handle_tts_playback(update, answer)
        update_memory(user_id, prompt, answer)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка ответа: {e}")

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
            await update.message.reply_voice(voice=audio_file)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка TTS: {e}")

# 📢 Озвучка через кнопку
async def handle_tts_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_tts:
        return
    text = update.message.text.strip()
    if not text:
        await update.message.reply_text("⚠️ Пожалуйста, отправьте текст.")
        return
    if contains_prohibited_content(text):
        await update.message.reply_text("🚫 Обнаружен недопустимый или опасный запрос. Попробуй переформулировать.")
        return
    await handle_tts_playback(update, text)
    active_tts.discard(user_id)

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

try:
    from utils.google_sheets import log_translation, log_gpt
except ImportError:
    log_translation = lambda *args, **kwargs: None
    log_gpt = lambda *args, **kwargs: None

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
user_histories = {}

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
        await update.message.reply_text(f"📝 Распознано:
{text}")

        if user_id not in notified_voice_users:
            notified_voice_users.add(user_id)
            await update.message.reply_text(
                "💡 Ты можешь просто говорить команды:
"
                "• «Переведи на русский язык I love you»
"
                "• «Сгенерируй картинку»
"
                "• «Озвучь текст»
"
                "• «Объясни что такое...»

"
                "Я сама включу нужный режим 🤖"
            )

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
            await update.message.reply_text("🤖 Думаю...
📸 Включён режим генерации. Опиши изображение.")
            return

        if any(word in lower for word in ["объясни", "что такое", "вопрос", "?"]):
            clear_user_state(user_id)
            active_ask.add(user_id)
            await reply_with_gpt(update, text)
            return

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# 🤖 Ответ с использованием GPT и озвучкой
async def reply_with_gpt(update: Update, question: str):
    await update.message.reply_text("🧠 Думаю...")

    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    history = user_histories.get(user_id, [])

    try:
        messages = [{"role": "system", "content": "Ты дружелюбный голосовой помощник AniAI."}]
        messages.extend(history[-6:])
        messages.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        answer = response.choices[0].message.content.strip()

        await handle_tts_playback(update, answer)
        user_histories[user_id] = history[-6:] + [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
        log_gpt(user_id, full_name, question, answer)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка GPT: {e}")

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
        await update.message.reply_text(f"🌍 Перевод:
{translation}")
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

# 📢 Озвучка через команду /tts
async def handle_tts_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("🔊 Введите текст после команды /tts.")
        return
    await handle_tts_playback(update, text)

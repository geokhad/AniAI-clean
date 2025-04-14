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
from collections import defaultdict

try:
    from utils.google_sheets import log_translation, log_gpt
except ImportError:
    log_translation = lambda *args, **kwargs: None
    log_gpt = lambda *args, **kwargs: None

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
user_dialogues = defaultdict(list)

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

        if user_id not in notified_voice_users:
            notified_voice_users.add(user_id)
            await update.message.reply_text(
                "💡 Ты можешь просто говорить команды:\n"
                "• «Переведи на русский язык I love you»\n"
                "• «Сгенерируй картинку»\n"
                "• «Озвучь текст»\n"
                "• «Объясни что такое...»\n\n"
                "Я сама включу нужный режим 🤖"
            )

        # 🧠 Авто-GPT для вопросительных конструкций
        if text.endswith("?") or any(q in lower for q in ["что", "зачем", "почему", "как", "когда", "где", "кто"]):
            await update.message.reply_text("🤔 Думаю над ответом...")
            await answer_with_gpt(update, user_id, text)
            return

        if "переведи на русский" in lower:
            prompt = text.split("переведи на русский", 1)[-1].strip()
            await translate_and_reply(update, prompt, "на русский")
            return

        if "переведи на английский" in lower:
            prompt = text.split("переведи на английский", 1)[-1].strip()
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

        if any(word in lower for word in ["картинку", "изображение", "сгенерируй", "создай", "изобрази"]):
            clear_user_state(user_id)
            active_imagers.add(user_id)
            await update.message.reply_text("🤖 Думаю...\n📸 Включён режим генерации. Опиши изображение.")
            return

        if any(word in lower for word in ["объясни", "вопрос", "что такое"]):
            clear_user_state(user_id)
            active_ask.add(user_id)
            await update.message.reply_text("🧠 Включён режим GPT. Задай свой вопрос.")
            return

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка распознавания речи: {e}")

# 🧠 Ответ через GPT с логированием
async def answer_with_gpt(update: Update, user_id: int, user_text: str):
    user_name = update.effective_user.full_name
    messages = user_dialogues[user_id][-6:]  # сохраняем только последние 6 для памяти

    dialogue = [{"role": "system", "content": "Ты умная помощница, отвечающая понятно и с заботой."}]
    for m in messages:
        dialogue.append({"role": "user", "content": m["q"]})
        dialogue.append({"role": "assistant", "content": m["a"]})
    dialogue.append({"role": "user", "content": user_text})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=dialogue
        )
        answer = response.choices[0].message.content.strip()

        # Сохраняем в память
        user_dialogues[user_id].append({"q": user_text, "a": answer})
        user_dialogues[user_id] = user_dialogues[user_id][-10:]

        # Озвучка ответа
        await handle_tts_playback(update, answer)

        # Логируем
        log_gpt(user_id, user_name, user_text, answer)

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка при генерации ответа: {e}")

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
            await update.message.reply_voice(voice=audio_file)
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка TTS: {e}")

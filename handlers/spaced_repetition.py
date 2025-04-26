from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
import os
from datetime import date, timedelta
from openai import OpenAI
from utils.spaced_words import spaced_words
from utils.google_sheets import log_voa_word
from utils.spaced_memory import update_word_memory
from utils.voice_tools import recognize_speech_from_voice

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Активные пользователи
active_voa = set()
user_words = {}

# ▶️ Стартовая точка (интервальное повторение по spaced_words)
async def start_spaced_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().isoformat()

    due_words = [word for word in spaced_words if word["next_review"] <= today]
    if not due_words:
        if update.message:
            await update.message.reply_text("✅ Нет слов для повторения сегодня! Отличная работа!")
        elif update.callback_query:
            await update.callback_query.message.reply_text("✅ Нет слов для повторения сегодня! Отличная работа!")
        return

    word_data = random.choice(due_words)
    user_id = update.effective_user.id
    user_words[user_id] = word_data
    active_voa.add(user_id)

    audio = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=word_data['word']
    )
    path = f"/tmp/voa-{user_id}.ogg"
    with open(path, "wb") as f:
        f.write(audio.content)

    if update.message:
        chat_id = update.message.chat.id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
    else:
        return

    with open(path, "rb") as audio_file:
        await context.bot.send_voice(chat_id=chat_id, voice=audio_file)

    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"✏️ Type or say the word you hear...\n\n"
            f"📘 Level: {word_data['level']}\n"
            f"📚 Topic: {word_data['topic']}"
        ),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ I know it", callback_data="vocab_remember")],
            [InlineKeyboardButton("🔁 Repeat word", callback_data="vocab_repeat")]
        ])
    )

# 🧠 Проверка текстового ответа
async def handle_voa_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = update.message.text.strip().lower()
    expected = user_words[user_id]['word'].lower()

    if text == expected:
        await update.message.reply_text("✅ Correct! Well done.")
        await update_word_progress(user_id)
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{expected}</b>", parse_mode="HTML")

    await show_definition(update, user_words[user_id])
    log_voa_word(user_id, update.effective_user.full_name, user_words[user_id]['word'])
    active_voa.discard(user_id)

# 🎙 Проверка голосового ответа
async def handle_voa_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = await recognize_speech_from_voice(update, context)
    if text:
        update.message.text = text
        await handle_voa_text(update, context)
    else:
        await update.message.reply_text("⚠️ Sorry, I couldn't recognize your voice. Please try again.")

# 📖 Показ определения и примера
async def show_definition(update: Update, word_data: dict):
    await update.message.reply_text(
        f"📖 <b>{word_data['word'].capitalize()}</b> ({word_data['level']}, {word_data['topic']})\n"
        f"📝 {word_data['definition']}\n"
        f"💬 Example: {word_data['example']}",
        parse_mode="HTML"
    )

# ✅ Обновление прогресса после правильного ответа
async def update_word_progress(user_id):
    today = date.today()

    word = user_words[user_id]
    word["interval_stage"] += 1
    days_to_next = 2 ** word["interval_stage"]
    next_review_date = today + timedelta(days=days_to_next)

    word["last_review"] = today.isoformat()
    word["next_review"] = next_review_date.isoformat()

    update_word_memory(user_id, word["word"])  # Логирование или обновление записи

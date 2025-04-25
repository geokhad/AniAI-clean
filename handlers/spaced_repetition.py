import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from openai import OpenAI
from handlers.state import active_voa
from utils.spaced_words import spaced_words
from utils.google_sheets import log_voa_word
from utils.voice_tools import recognize_speech_from_voice, speak_text

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Хранение текущего слова на пользователя
user_words = {}

# ▶️ Стартовая точка
async def start_spaced_repetition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    word_data = random.choice(spaced_words)
    user_words[user_id] = word_data
    active_voa.add(user_id)

    await speak_text(update, word_data['word'])

    keyboard = [
        [
            InlineKeyboardButton("🔁 Repeat", callback_data="voa_repeat"),
            InlineKeyboardButton("✅ Got it", callback_data="voa_remember")
        ]
    ]

    await update.message.reply_text(
        f"✏️ Type or say the word you hear...\n\n"
        f"📘 Level: {word_data['level']}\n📚 Topic: {word_data['topic']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 📘 Обработка текстового ответа
async def handle_voa_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = update.message.text.strip().lower()
    expected = user_words[user_id]['word'].lower()

    if text == expected:
        await update.message.reply_text("✅ Correct! Well done.")
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{expected}</b>", parse_mode="HTML")

    await show_definition(update, user_words[user_id])
    log_voa_word(user_id, update.effective_user.full_name, user_words[user_id]['word'])
    active_voa.discard(user_id)

# 🎙 Обработка голосового ввода
async def handle_voa_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = await recognize_speech_from_voice(update, context)
    update.message.text = text
    await handle_voa_text(update, context)

# 📘 Показ определения и примера
async def show_definition(update: Update, word_data: dict):
    await update.message.reply_text(
        f"📖 <b>{word_data['word'].capitalize()}</b> ({word_data['level']}, {word_data['topic']})\n"
        f"📝 {word_data['definition']}\n"
        f"💬 Example: {word_data['example']}",
        parse_mode="HTML"
    )

# ⌨️ Обработка кнопок
async def handle_voa_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_words:
        await query.message.reply_text("⚠️ No word found. Please start again: /voa")
        return

    if query.data == "voa_repeat":
        await speak_text(update, user_words[user_id]['word'])
        await query.message.reply_text("🔁 Repeated. Now try again!")

    elif query.data == "voa_remember":
        log_voa_word(user_id, query.from_user.full_name, user_words[user_id]['word'])
        active_voa.discard(user_id)
        await query.message.reply_text("👍 Great! Let’s try another one.")
        await start_spaced_repetition(update, context)

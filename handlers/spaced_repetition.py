from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.spaced_words import spaced_words
from utils.google_sheets import log_voa_word, log_voa_memory
from utils.spaced_memory import update_word_memory
from utils.voice_tools import recognize_speech_from_voice, speak_text
import random

# Активные пользователи и их текущие слова
active_voa = set()
user_words = {}

# ▶️ Старт: запуск упражнений
async def start_spaced_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    word_data = random.choice(spaced_words)
    user_words[user_id] = word_data
    active_voa.add(user_id)

    # Озвучка слова
    await speak_text(update, word_data['word'])

    # Отправляем подсказку
    keyboard = [
        [InlineKeyboardButton("✅ I remember", callback_data="vocab_remember")],
        [InlineKeyboardButton("🔁 Repeat", callback_data="vocab_repeat")]
    ]
    await update.message.reply_text(
        f"✏️ Type or say the word you hear...\n\n"
        f"📘 Level: {word_data['level']}\n"
        f"📚 Topic: {word_data['topic']}",
        reply_markup=InlineKeyboardMarkup(keyboard)
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
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{expected}</b>", parse_mode="HTML")

    await show_definition(update, user_words[user_id])
    log_voa_word(user_id, update.effective_user.full_name, user_words[user_id]['word'])
    update_word_memory(user_id, user_words[user_id]['word'], success=(text == expected))
    active_voa.discard(user_id)

# 🎙 Обработка голосового ответа
async def handle_voa_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = await recognize_speech_from_voice(update, context)
    if text:
        update.message.text = text
        await handle_voa_text(update, context)
    else:
        await update.message.reply_text("⚠️ Could not recognize the voice message. Please try again.")

# 📖 Показать определение и пример
async def show_definition(update: Update, word_data: dict):
    await update.message.reply_text(
        f"📖 <b>{word_data['word'].capitalize()}</b> ({word_data['level']}, {word_data['topic']})\n"
        f"📝 {word_data['definition']}\n"
        f"💬 Example: {word_data['example']}",
        parse_mode="HTML"
    )

# 📋 Обработка кнопок
async def handle_vocab_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "vocab_remember":
        await query.message.reply_text("🎯 Great! Let's do another one!")
        await start_spaced_vocab(update, context)
    elif query.data == "vocab_repeat":
        if user_id in user_words:
            await speak_text(update, user_words[user_id]['word'])
            await query.message.reply_text(
                f"🔁 Repeating...\n\n"
                f"📘 Level: {user_words[user_id]['level']}\n"
                f"📚 Topic: {user_words[user_id]['topic']}"
            )

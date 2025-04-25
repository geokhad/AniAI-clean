from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.spaced_words import spaced_words
from utils.spaced_memory import update_word_memory
from utils.google_sheets import log_voa_word, log_voa_memory
from utils.voice_tools import recognize_speech_from_voice
from openai import OpenAI
import os
import random

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Активные пользователи
active_voa = set()
user_words = {}

# ▶️ Стартовая точка
async def start_spaced_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    word_data = random.choice(spaced_words)
    user_words[user_id] = word_data
    active_voa.add(user_id)

    # Генерация озвучки
    audio = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=word_data['word']
    )
    path = f"/tmp/voa-{user_id}.ogg"
    with open(path, "wb") as f:
        f.write(audio.content)

    with open(path, "rb") as audio_file:
        await update.message.reply_voice(voice=audio_file)

    await update.message.reply_text(
        f"✏️ Type or say the word you hear...\n\n"
        f"📘 Level: {word_data['level']} | 📚 Topic: {word_data['topic']}"
    )

# 📘 Показ определения и примера
async def show_definition(update: Update, word_data: dict):
    text = (
        f"📖 <b>{word_data['word'].capitalize()}</b> ({word_data['level']}, {word_data['topic']})\n"
        f"📝 {word_data['definition']}\n"
        f"💬 Example: {word_data['example']}"
    )
    keyboard = [
        [InlineKeyboardButton("✅ I remember this", callback_data="vocab_remember")],
        [InlineKeyboardButton("🔁 Repeat again", callback_data="vocab_repeat")]
    ]
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

# 🎤 Обработка голосового сообщения
async def handle_voa_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = await recognize_speech_from_voice(update, context)
    update.message.text = text  # Используем тот же хендлер, что и для текста
    await handle_voa_text(update, context)

# ⌨️ Обработка текстового ввода
async def handle_voa_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    user_input = update.message.text.strip().lower()
    expected = user_words[user_id]['word'].lower()

    if user_input == expected:
        await update.message.reply_text("✅ Correct! Well done.")
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{expected}</b>", parse_mode="HTML")

    await show_definition(update, user_words[user_id])
    log_voa_word(user_id, update.effective_user.full_name, user_words[user_id]['word'])
    update_word_memory(user_id, user_words[user_id]['word'], user_input == expected)
    active_voa.discard(user_id)

# 🎛 Обработка кнопок
async def handle_vocab_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_words:
        await query.message.reply_text("❗ Start the vocabulary session again: /spaced")
        return

    if query.data == "vocab_remember":
        await query.message.reply_text("👍 Great! Let’s do another one:")
        await start_spaced_vocab(update, context)

    elif query.data == "vocab_repeat":
        await query.message.reply_text("🔁 No worries, try again:")
        await start_spaced_vocab(update, context)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
import os
from openai import OpenAI
from utils.spaced_words import spaced_words
from utils.spaced_memory import update_word_memory
from utils.google_sheets import log_voa_word
from utils.voice_tools import recognize_speech_from_voice, speak_text
from handlers.state import active_voa

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Текущее слово для каждого пользователя
user_words = {}

# ▶️ Начало сессии spaced vocab
async def start_spaced_vocab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    word_data = random.choice(spaced_words)
    user_words[user_id] = word_data
    active_voa.add(user_id)

    await speak_text(update, word_data['word'])

    keyboard = [
        [InlineKeyboardButton("✏️ Type the word", callback_data="type_word")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📘 Listen to the word and type or say it!",
        reply_markup=reply_markup
    )

# 📝 Обработка текстового ответа
async def handle_voa_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    text = update.message.text.strip().lower()
    expected = user_words[user_id]['word'].lower()

    if text == expected:
        await update.message.reply_text("✅ Correct! Well done.")
        update_word_memory(user_id, expected, success=True)
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{expected}</b>", parse_mode="HTML")
        update_word_memory(user_id, expected, success=False)

    log_voa_word(user_id, update.effective_user.full_name, expected)
    await show_definition(update, user_words[user_id])
    active_voa.discard(user_id)

# 🎤 Обработка голосового ответа
async def handle_voa_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa:
        return

    recognized_text = await recognize_speech_from_voice(update, context)
    update.message.text = recognized_text  # Переиспользуем
    await handle_voa_text(update, context)

# 📖 Показать определение и пример
async def show_definition(update: Update, word_data: dict):
    await update.message.reply_text(
        f"🔖 <b>{word_data['word'].capitalize()}</b> ({word_data['level']}, {word_data['topic']})\n"
        f"📖 {word_data['definition']}\n"
        f"💬 Example: {word_data['example']}",
        parse_mode="HTML"
    )

# 🌐 Голосовая озвучка слова через OpenAI
async def speak_text(update: Update, word: str):
    user_id = update.effective_user.id
    audio = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=word
    )
    path = f"/tmp/voa-{user_id}.ogg"
    with open(path, "wb") as f:
        f.write(audio.content)

    with open(path, "rb") as audio_file:
        await update.message.reply_voice(voice=audio_file)

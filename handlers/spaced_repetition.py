from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
import os
from openai import OpenAI
from utils.spaced_words import spaced_words
from utils.google_sheets import log_voa_word, log_voa_memory
from utils.spaced_memory import update_word_memory
from utils.voice_tools import recognize_speech_from_voice

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
        return  # Безопасный выход, если что-то не так

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
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{expected}</b>", parse_mode="HTML")

    await show_definition(update, user_words[user_id])
    log_voa_word(user_id, update.effective_user.full_name, user_words[user_id]['word'])
    update_word_memory(user_id, user_words[user_id]['word'])
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

# 📚 Обработка нажатий кнопок
async def handle_vocab_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if user_id not in user_words:
        await query.message.reply_text("❗ Start spaced repetition first: /spaced")
        return

    if query.data == "vocab_repeat":
        await start_spaced_vocab(update, context)
        return

    if query.data == "vocab_remember":
        await query.message.reply_text("👍 Great! Let's practice another word!")
        await start_spaced_vocab(update, context)
        return

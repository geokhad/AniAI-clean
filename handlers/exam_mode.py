
from telegram import Update
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
active_voa_exam = set()
user_exam_words = {}

# ▶️ Запуск VOA exam: бот показывает определение, а не само слово
async def start_voa_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().isoformat()
    due_words = [word for word in spaced_words if word["next_review"] <= today]
    if not due_words:
        await update.message.reply_text("✅ No words to review today. Great job!")
        return

    word_data = random.choice(due_words)
    user_id = update.effective_user.id
    user_exam_words[user_id] = word_data
    active_voa_exam.add(user_id)

    await update.message.reply_text(
        f"📘 Level: {word_data['level']}
"
        f"📚 Topic: {word_data['topic']}

"
        f"🧠 Definition: {word_data['definition']}

"
        f"🎙 Say or type the word that matches this definition:"
    )

# 🧠 Обработка текстового ответа в exam-режиме
async def handle_voa_text_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa_exam:
        return

    user_input = update.message.text.strip().lower()
    correct_word = user_exam_words[user_id]["word"].lower()

    if user_input == correct_word:
        await update.message.reply_text("✅ Correct! Well done.")
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{correct_word}</b>", parse_mode="HTML")

    await show_exam_example(update, user_exam_words[user_id])
    log_voa_word(user_id, update.effective_user.full_name, correct_word)
    update_word_memory(user_id, correct_word)
    active_voa_exam.discard(user_id)

# 🎙 Обработка голосового ответа
async def handle_voa_voice_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa_exam:
        return

    text = await recognize_speech_from_voice(update, context)
    if text:
        update.message.text = text
        await handle_voa_text_exam(update, context)
    else:
        await update.message.reply_text("⚠️ Sorry, I couldn't recognize your voice. Please try again.")

# 📖 Показ примера
async def show_exam_example(update: Update, word_data: dict):
    await update.message.reply_text(
        f"💬 Example: {word_data['example']}",
        parse_mode="HTML"
    )


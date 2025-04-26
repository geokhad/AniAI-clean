from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import random
import os
from datetime import date
from openai import OpenAI
from utils.spaced_words import spaced_words
from utils.google_sheets import log_voa_word
from utils.spaced_memory import update_word_memory
from utils.voice_tools import recognize_speech_from_voice

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Активные пользователи в экзамене
active_voa_exam = set()
user_exam_words = {}

# ▶️ Старт экзамена VOA
async def start_voa_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = date.today().isoformat()
    due_words = [word for word in spaced_words if word["next_review"] <= today]
    if not due_words:
        if update.callback_query:
            await update.callback_query.message.reply_text("✅ No words to review today. Great job!")
        else:
            await update.message.reply_text("✅ No words to review today. Great job!")
        return

    word_data = random.choice(due_words)
    user_id = update.effective_user.id
    user_exam_words[user_id] = word_data
    active_voa_exam.add(user_id)

    target = update.callback_query.message if update.callback_query else update.message

    await target.reply_text(
        f"📘 Level: {word_data['level']}\n"
        f"📚 Topic: {word_data['topic']}\n\n"
        f"🧠 Definition: {word_data['definition']}\n\n"
        f"🎙 Say or type the word that matches this definition:"
    )

# 📝 Обработка текстового ответа
async def handle_voa_text_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa_exam:
        return

    text = update.message.text.strip().lower()
    await check_voa_answer(update, context, user_id, text)

# 🎤 Обработка голосового ответа
async def handle_voa_voice_exam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_voa_exam:
        return

    text = await recognize_speech_from_voice(update, context)
    if text:
        await check_voa_answer(update, context, user_id, text.lower())
    else:
        await update.message.reply_text("⚠️ Sorry, I couldn't recognize your voice. Please try again.")

# ✅ Проверка ответа пользователя
async def check_voa_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, text: str):
    correct_word = user_exam_words[user_id]["word"].lower()

    if text == correct_word:
        await update.message.reply_text("✅ Correct! Well done.")
    else:
        await update.message.reply_text(f"❌ Not quite. The correct word was: <b>{correct_word}</b>", parse_mode="HTML")

    await show_exam_example(update, user_exam_words[user_id])

    log_voa_word(user_id, update.effective_user.full_name, correct_word)
    update_word_memory(user_id, correct_word)

    active_voa_exam.discard(user_id)

    # Кнопка ➡️ "Следующее слово"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➡️ Следующее слово", callback_data="voa_next")]
    ])
    await update.message.reply_text(
        "Готов к следующему слову? Нажми кнопку!",
        reply_markup=keyboard
    )

# 📖 Показ примера использования слова
async def show_exam_example(update: Update, word_data: dict):
    await update.message.reply_text(
        f"💬 Example: {word_data['example']}",
        parse_mode="HTML"
    )

# 🎯 Обработка нажатия "Следующее слово"
async def handle_voa_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Прямая переотправка на новый вопрос
    await start_voa_exam(update, context)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from questions import questions
import random

# Словарь, в котором хранятся текущие вопросы пользователей
active_quizzes = {}

# 📘 Отправка теста
async def start_daily_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    question = random.choice(questions)
    active_quizzes[user_id] = question

    keyboard = [[InlineKeyboardButton(opt, callback_data=f"daily_answer|{opt}")] for opt in question["options"]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await (update.message or update.callback_query.message).reply_text(
        f"📝 <b>Question 1:</b>\n{question['question']}\n\n💬 Example: {question['example']}",
        parse_mode="HTML",
        reply_markup=reply_markup
    )

# 📘 Обработка ответа
async def handle_daily_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data.split("|", 1)

    if len(data) != 2:
        await query.message.reply_text("⚠️ Неверный формат ответа.")
        return

    selected = data[1]
    question = active_quizzes.get(user_id)

    if not question:
        await query.message.reply_text("⚠️ Вопрос не найден. Пожалуйста, начни заново через /menu.")
        return

    correct = question["answer"]
    explanation = question.get("explanation", "")

    if selected == correct:
        reply = f"✅ Правильно!\n\n📘 Объяснение: {explanation}"
    else:
        reply = f"❌ Неправильно.\nПравильный ответ: <b>{correct}</b>\n\n📘 Объяснение: {explanation}"

    del active_quizzes[user_id]

    keyboard = [[InlineKeyboardButton("📝 Daily English", callback_data="daily_english")]]
    await query.message.reply_text(reply, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard))

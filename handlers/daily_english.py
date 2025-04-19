import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.questions import questions

# Сколько вопросов за раз
DAILY_QUESTION_COUNT = 3

# Храним активные вопросы в контексте
user_daily_questions = {}

# Кнопка запуска викторины
async def start_daily_english(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Выбираем случайные вопросы
    selected = random.sample(questions, DAILY_QUESTION_COUNT)
    user_daily_questions[user_id] = selected

    await send_question(update, context, user_id, question_index=0)


async def send_question(update, context, user_id, question_index):
    question = user_daily_questions[user_id][question_index]
    options = question['options']

    buttons = [[InlineKeyboardButton(opt, callback_data=f"daily_{question_index}_{opt}")] for opt in options]
    
    text = f"📝 <b>Question {question_index + 1}:</b>\n{question['question']}"

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode="HTML"
    )


# Обработка ответа пользователя
async def handle_daily_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    data = query.data  # format: daily_0_to continue
    _, q_index_str, selected = data.split("_", 2)
    q_index = int(q_index_str)

    question = user_daily_questions.get(user_id, [])[q_index]
    correct = question['answer']

    if selected == correct:
        feedback = "✅ <b>Правильно!</b>"
    else:
        feedback = f"❌ <b>Неверно.</b> Правильный ответ: <i>{correct}</i>"

    explanation = f"\n💡 {question['explanation']}\n📚 Пример: {question['example']}"
    await query.edit_message_text(text=feedback + explanation, parse_mode="HTML")

    # Отправим следующий вопрос, если есть
    if q_index + 1 < DAILY_QUESTION_COUNT:
        await send_question(update, context, user_id, q_index + 1)
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎉 Готово! Возвращайся завтра за новыми словами.")

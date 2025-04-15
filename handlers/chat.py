from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_ask
from utils.google_sheets import log_gpt
from datetime import datetime, timedelta

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Сеансовая память: user_id → список сообщений
session_memory = {}
last_interaction = {}

# Константы
MAX_SESSION_LENGTH = 5
SESSION_TIMEOUT = timedelta(minutes=10)

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❓ Введите вопрос после команды /ask")
        return

    user_id = update.effective_user.id
    active_ask.add(user_id)
    await send_gpt_response(update, prompt)

async def handle_gpt_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_ask:
        return

    prompt = update.message.text.strip()
    await send_gpt_response(update, prompt)

async def send_gpt_response(update: Update, prompt: str):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    now = datetime.now()

    # Проверка тайм-аута
    if user_id in last_interaction:
        if now - last_interaction[user_id] > SESSION_TIMEOUT:
            session_memory[user_id] = []

    last_interaction[user_id] = now

    # Получаем историю
    history = session_memory.get(user_id, [])
    history.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=history
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)

        # Добавляем в память и обрезаем до последних MAX_SESSION_LENGTH*2 сообщений (вопрос-ответ)
        history.append({"role": "assistant", "content": answer})
        session_memory[user_id] = history[-MAX_SESSION_LENGTH*2:]

        # Логируем
        log_gpt(
            user_id=user_id,
            full_name=full_name,
            question=prompt,
            answer=answer
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка от GPT: {e}")

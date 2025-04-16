from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_ask
from utils.google_sheets import log_gpt
from utils.memory import get_memory, update_memory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Команда /ask
async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❓ Введите вопрос после команды /ask")
        return

    user_id = update.effective_user.id
    active_ask.add(user_id)

    await send_gpt_response(update, prompt)

# Продолжение GPT-диалога
async def handle_gpt_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_ask:
        return

    prompt = update.message.text.strip()
    await send_gpt_response(update, prompt)

# Основная логика: генерация ответа и работа с памятью
async def send_gpt_response(update: Update, prompt: str):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    try:
        # Загружаем сеансовую память
        memory = get_memory(user_id)

        # Начинаем с системного промта
        messages = [{"role": "system", "content": "Ты — полезный Telegram-ассистент. Отвечай понятно, кратко и дружелюбно."}]

        # Добавляем историю из памяти
        for q, a in memory:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})

        # Добавляем текущий вопрос
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)

        # Обновляем память
        update_memory(user_id, prompt, answer)

        # Логируем в Google Sheets
        log_gpt(
            user_id=user_id,
            full_name=full_name,
            question=prompt,
            answer=answer
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка от GPT: {e}")

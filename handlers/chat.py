from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_ask
from utils.google_sheets import log_gpt
from utils.memory import get_memory, update_memory

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🚫 Нецензурная лексика и запрещённые темы
BANNED_WORDS = [
    "хуй", "пизда", "блядь", "ебать", "нахуй", "сука", "уёбок", "мудила",
    "террор", "террорист", "теракт", "убийство", "насилие", "изнасилование",
    "война", "украин", "русск", "путин", "зеленск", "москал", "оккупант"
]

def contains_banned_words(text):
    lower = text.lower()
    return any(word in lower for word in BANNED_WORDS)

# Команда /ask
async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❓ Введите вопрос после команды /ask")
        return

    if contains_banned_words(prompt):
        await update.message.reply_text("🚫 Извините, этот запрос нарушает правила использования.")
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

    if contains_banned_words(prompt):
        await update.message.reply_text("🚫 Извините, этот запрос нарушает правила использования.")
        return

    await send_gpt_response(update, prompt)

# Основная логика: генерация ответа и работа с памятью
async def send_gpt_response(update: Update, prompt: str):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name

    try:
        memory = get_memory(user_id)
        messages = [{"role": "system", "content": "Ты — полезный Telegram-ассистент. Отвечай понятно, кратко и дружелюбно."}]

        for q, a in memory:
            messages.append({"role": "user", "content": q})
            messages.append({"role": "assistant", "content": a})

        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        answer = response.choices[0].message.content.strip()
        await update.message.reply_text(answer)

        update_memory(user_id, prompt, answer)

        log_gpt(
            user_id=user_id,
            full_name=full_name,
            question=prompt,
            answer=answer
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка от GPT: {e}")

from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_ask  # ✅ Состояние
from utils.google_sheets import log_gpt  # ✅ Добавлено логирование

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❓ Введите вопрос после команды /ask")
        return

    # Активируем режим GPT-помощи
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

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

        # ✅ Логирование запроса в Google Sheets
        log_gpt(
            user_id=user_id,
            full_name=full_name,
            question=prompt,
            answer=answer
        )

    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка от GPT: {e}")

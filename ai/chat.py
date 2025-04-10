from telegram import Update
from telegram.ext import ContextTypes
from openai import OpenAI
from utils.google_sheets import log_gpt

import os

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

async def handle_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = ' '.join(context.args)
    user = update.effective_user

    if not user_input:
        await update.message.reply_text("❓ Введите вопрос после команды /ask")
        return

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        temperature=0.7
    )
    answer = response.choices[0].message.content.strip()
    await update.message.reply_text(answer)
    
    log_gpt(user.id, user.full_name, user_input, answer, lang="ru")
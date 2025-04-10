from telegram import Update
from telegram.ext import ContextTypes
from utils.google_sheets import log_subscriber

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_subscriber(user.id, user.full_name, user.username)
    await update.message.reply_text("👋 Привет! Я AniAI. Напиши /ask и свой вопрос.")
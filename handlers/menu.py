from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 Задать вопрос", switch_inline_query_current_chat="")],
        [InlineKeyboardButton("✍️ Оставить отзыв", url="https://t.me/AniAI_newbot")],
        [InlineKeyboardButton("🚀 Запустить AniAI", url="https://t.me/AniAI_newbot")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите действие:", reply_markup=reply_markup)


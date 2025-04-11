from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("🗣 Голосовой режим", callback_data="voice_mode")],
        [InlineKeyboardButton("🌐 Сменить язык", callback_data="change_language")],
        [InlineKeyboardButton("💎 Премиум режим", callback_data="premium_mode")],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="leave_feedback")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 Главное меню AniAI:", reply_markup=reply_markup)

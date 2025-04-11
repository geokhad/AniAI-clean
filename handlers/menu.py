from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = (
        update.effective_chat.id if update.message
        else update.callback_query.message.chat.id
    )

    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("🎙 Голосовой режим", callback_data="voice_mode")],
        [InlineKeyboardButton("🌐 Сменить язык", callback_data="change_lang")],
        [InlineKeyboardButton("💎 Премиум режим", callback_data="premium")],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="feedback")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text="📋 Главное меню AniAI:",
        reply_markup=reply_markup
    )

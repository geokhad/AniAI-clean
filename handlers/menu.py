from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📋 Главное меню AniAI:")

    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("🎙 Голосовой режим", callback_data="voice_mode")],
        [InlineKeyboardButton("🌐 Сменить язык", callback_data="change_language")],
        [InlineKeyboardButton("💎 Премиум режим", callback_data="premium_mode")],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="feedback")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выберите действие:",
        reply_markup=reply_markup
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    response_map = {
        "gpt_help": "🧠 Напиши свой вопрос, и AniAI постарается помочь!",
        "voice_mode": "🎙 Голосовой режим пока в разработке...",
        "change_language": "🌐 Вы можете выбрать язык: Русский / English (временно только русский).",
        "premium_mode": "💎 Премиум-режим будет доступен в следующем обновлении.",
        "feedback": "✍️ Напишите отзыв в свободной форме. Мы читаем каждый!",
    }

    response = response_map.get(query.data, "⚙️ Функция в разработке.")
    await context.bot.send_message(chat_id=query.message.chat.id, text=response)

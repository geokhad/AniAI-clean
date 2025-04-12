from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("📚 Примеры запросов", callback_data="examples")],
        [InlineKeyboardButton("🎙 Голосовой режим", callback_data="voice_mode")],
        [InlineKeyboardButton("🌐 Переключить язык (временно недоступно)", callback_data="change_language")],
        [InlineKeyboardButton("💎 Премиум режим", callback_data="premium_mode")],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="feedback")],
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📋 Главное меню AniAI:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_menu":
        intro = """🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который поможет тебе в работе,
учёбе и повседневной жизни!

Примеры команд:
• Сгенерируй изображение города будущего
• Переведи текст на французский
• Напиши описание продукта для маркетплейса

👇 Ниже доступно главное меню"""
        await context.bot.send_message(chat_id=query.message.chat.id, text=intro)
        await menu(update, context)
        return

    responses = {
        "gpt_help": """🧠 Чтобы задать вопрос, используй команду:
/ask Твой вопрос

Например:
/ask Объясни, как работает фотосинтез простыми словами""",
        "examples": """📚 Примеры запросов:
• Сгенерируй изображение города на Марсе в стиле киберпанк
• Создай музыку в стиле lo-fi для работы
• Объясни квантовую запутанность простыми словами
• Переведи этот текст на английский: "Спасибо за помощь"

👉 Используй /ask перед вопросом""",
        "voice_mode": "🎙 Голосовой режим пока в разработке...",
        "change_language": "🌐 Переключение языка будет доступно позже. Сейчас доступен только русский язык.",
        "premium_mode": "💎 Премиум-режим будет доступен в следующем обновлении.",
        "feedback": """📬 Оставьте отзыв здесь: @AniAI_supportbot
Мы читаем каждый отклик!"""
    }

    response = responses.get(query.data)
    if response:
        await context.bot.send_message(chat_id=query.message.chat.id, text=response)
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Функция в разработке.")

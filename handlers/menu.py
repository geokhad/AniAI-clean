from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("📚 Примеры запросов", callback_data="examples")],
        [InlineKeyboardButton("📸 Сгенерировать изображение", callback_data="image_help")],
        [InlineKeyboardButton("📄 Проанализировать документ", callback_data="analyze_help")],
        [InlineKeyboardButton("🌍 Перевести текст", callback_data="translate")],
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
        intro = (
            "🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который поможет тебе в работе, учёбе и повседневной жизни!\n\n"
            "С AniAI ты получаешь быстрый и простой доступ к самым мощным нейросетям прямо в Telegram. Просто напиши свой запрос — и бот сам разберётся, что тебе нужно:\n\n"
            "✨ Примеры:\n"
            "• Сгенерируй изображение города на Марсе в стиле киберпанк\n"
            "• Сделай краткое содержание документа (и прикрепи PDF или текст)\n"
            "• Напиши поздравление коллеге\n"
            "• Создай музыку в стиле lo-fi\n"
            "• Переведи текст на английский\n\n"
            "🤖 AniAI использует модели GPT-4o, DALL·E, Suno и другие.\n"
            "📆 Бесплатный доступ — 50 дней!\n\n"
            "👇 Главное меню:"
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text=intro)
        await menu(update, context)
        return

    responses = {
        "gpt_help": "🧠 Просто задай вопрос, и AniAI ответит. Например: «Объясни квантовую запутанность простыми словами»",
        "examples": (
            "📚 Примеры запросов:\n"
            "• Переведи текст на английский\n"
            "• Сгенерируй изображение замка\n"
            "• Объясни теорему Ферма\n"
            "• Придумай описание для поста\n"
            "• Составь план статьи"
        ),
        "translate": (
            "🌍 Просто отправь текст — AniAI переведёт с русского на английский или наоборот.\n"
            "📏 Лимит: до 3000 символов."
        ),
        "image_help": "📸 Напиши запрос — AniAI создаст изображение.\nНапример: «Замок в стиле стимпанк под луной»",
        "analyze_help": "📄 Прикрепи документ — AniAI выделит главное и сделает краткое резюме.",
        "voice_mode": "🎙 Голосовой режим в разработке. Поддержка аудио будет добавлена позже.",
        "change_language": "🌐 Переключение языка будет доступно в следующем обновлении.",
        "premium_mode": "💎 Премиум-режим включает GPT-4 и расширенные лимиты. Скоро будет доступен.",
        "feedback": "📬 Оставьте отзыв или пожелание здесь: @AniAI_supportbot"
    }

    response = responses.get(query.data)
    if response:
        await context.bot.send_message(chat_id=query.message.chat.id, text=response)
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Функция в разработке.")

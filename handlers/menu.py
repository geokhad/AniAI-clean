from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("🎙 Голосовой режим", callback_data="voice_mode")],
        [InlineKeyboardButton("🌐 Сменить язык", callback_data="change_language")],
        [InlineKeyboardButton("💎 Премиум режим", callback_data="premium_mode")],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="feedback")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="📋 Главное меню AniAI:", reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_menu":
        followup = """🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который поможет тебе в работе, учёбе и повседневной жизни!

С AniAI ты получаешь быстрый и простой доступ к самым мощным нейросетям прямо в Telegram. Просто напиши свой запрос — и бот сам разберётся, что тебе нужно:

✨ Примеры запросов:
• Сгенерируй изображение города на Марсе в стиле киберпанк
• Сделай краткое содержание документа (и прикрепи PDF или текст)
• Напиши поздравление с днём рождения коллеге в шуточном стиле
• Создай музыку в стиле lo-fi для работы
• Переведи текст на английский

Что умеет AniAI:
1. 📘 Объясняет сложные темы простым языком
2. ✍️ Помогает писать тексты, письма, описания
3. 🌍 Переводит на любой язык
4. 🖼 Генерирует иллюстрации и изображения
5. 🎵 Пишет музыку под настроение
6. 🎥 Создаёт короткие видео по сценарию
7. 📄 Анализирует документы и выделяет главное
8. 🔗 Ищет идеи, источники и вдохновение

🤖 AniAI использует самые передовые модели — GPT-4o, Ideogram, Suno и другие. Первый доступ бесплатный в течение 50 дней.

💬 Если возникнут вопросы или хочешь оставить отзыв — напиши в поддержку: @AniAI_supportbot"""
        await context.bot.send_message(chat_id=query.message.chat.id, text=followup)
        await menu(update, context)
        return

    if query.data == "gpt_help":
        help_text = (
            "🧠 Чтобы задать вопрос, используй команду:\n"
            "/ask Твой вопрос\n\n"
            "Например:\n"
            "/ask Объясни, как работает фотосинтез простыми словами"
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text=help_text)
        return

    if query.data == "feedback":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=(
                "📬 Оставьте ваш отзыв здесь: @AniAI_supportbot\n"
                "Мы читаем каждый отклик!"
            )
        )
        return

    response_map = {
        "voice_mode": "🎙 Голосовой режим пока в разработке...",
        "change_language": "🌐 Язык будет переключаем позже. Сейчас доступен только русский.",
        "premium_mode": "💎 Премиум-режим будет доступен в следующем обновлении.",
    }

    response = response_map.get(query.data, "⚙️ Функция в разработке.")
    await context.bot.send_message(chat_id=query.message.chat.id, text=response)

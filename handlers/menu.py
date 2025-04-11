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
        followup = """🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который помогает тебе в работе, учёбе и повседневной жизни.

С AniAI ты получаешь быстрый доступ к самым мощным нейросетям прямо в Telegram. Просто задай вопрос — и бот сам поймёт, чем помочь:

✨ Что можно попросить:
• Сгенерируй изображение города на Марсе в стиле киберпанк  
• Подведи итоги из PDF-документа или текста  
• Напиши шуточное поздравление коллеге  
• Создай музыку в стиле lo-fi для фона  
• Переведи текст на английский или любой язык

🛠 AniAI умеет:
1. 📘 Объяснять сложные темы простыми словами  
2. ✍️ Помогать с письмами, постами, статьями  
3. 🌍 Переводить тексты  
4. 🖼 Генерировать картинки и иллюстрации  
5. 🎵 Писать музыку по настроению  
6. 🎥 Создавать короткие видеоролики  
7. 📄 Анализировать документы и выделять главное  
8. 🔗 Искать идеи, ресурсы и вдохновение

🤖 Бот использует GPT-4o, Ideogram, Suno и другие передовые модели.  
🎁 Первые 50 дней — бесплатно.

Если возникнут вопросы или хочешь оставить отзыв — пиши в поддержку: @AniAI_supportbot
"""
        await context.bot.send_message(chat_id=query.message.chat.id, text=followup)
        await menu(update, context)
        return

    if query.data == "gpt_help":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
         text = (
    "🧠 Чтобы задать вопрос, используй команду:\n"
    "/ask Твой вопрос\n\n"
    "Например:\n"
    "/ask Объясни, как работает фотосинтез простыми словами"
)
        )
        return

    if query.data == "feedback":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📬 Оставьте ваш отзыв здесь: @AniAI_supportbot
Мы читаем каждый отклик!"
        )
        return

    response_map = {
        "voice_mode": "🎙 Голосовой режим пока в разработке...",
        "change_language": "🌐 Язык будет переключаем позже. Сейчас доступен только русский.",
        "premium_mode": "💎 Премиум-режим будет доступен в следующем обновлении.",
    }

    response = response_map.get(query.data, "⚙️ Функция в разработке.")
    await context.bot.send_message(chat_id=query.message.chat.id, text=response)

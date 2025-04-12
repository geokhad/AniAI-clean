from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("📚 Примеры запросов", callback_data="examples")],
        [InlineKeyboardButton("📸 Сгенерировать изображение", callback_data="image_help")],
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
        intro = """🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который поможет тебе в работе, учёбе и повседневной жизни!

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
        "translate": """🌍 Чтобы перевести текст, напиши:
/translate Твой текст

📏 Не более 3000 символов за раз""",
        "image_help": """📸 Чтобы сгенерировать изображение, используй команду:
/image Твой запрос

Примеры:
/image Летящий кот в очках на фоне заката
/image Замок в стиле стимпанк под луной

Модель: DALL·E 3. Размер: 1024x1024""",
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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.google_sheets import log_subscriber

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_subscriber(user.id, user.full_name, user.username)

    text = (
        "👋 Добро пожаловать в <b>AniAI</b> — интеллектуального ассистента для работы, учёбы и жизни!

"
        "🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который поможет тебе в работе, учёбе и повседневной жизни!

"
        "С AniAI ты получаешь быстрый и простой доступ к самым мощным нейросетям прямо в Telegram. Просто напиши свой запрос — и бот сам разберётся, что тебе нужно:

"
        "✨ Примеры запросов:
"
        "• Сгенерируй изображение города на Марсе в стиле киберпанк
"
        "• Сделай краткое содержание документа (и прикрепи PDF или текст)
"
        "• Напиши поздравление с днём рождения коллеге в шуточном стиле
"
        "• Создай музыку в стиле lo-fi для работы
"
        "• Переведи текст на английский

"
        "Что умеет AniAI:
"
        "1. 📘 Объясняет сложные темы простым языком
"
        "2. ✍️ Помогает писать тексты, письма, описания
"
        "3. 🌍 Переводит на любой язык
"
        "4. 🖼 Генерирует иллюстрации и изображения
"
        "5. 🎵 Пишет музыку под настроение
"
        "6. 🎥 Создаёт короткие видео по сценарию
"
        "7. 📄 Анализирует документы и выделяет главное
"
        "8. 🔗 Ищет идеи, источники и вдохновение

"
        "🤖 AniAI использует самые передовые модели — GPT-4o, Ideogram, Suno и другие. Первый доступ бесплатный в течение 50 дней.

"
        "💬 Если возникнут вопросы или хочешь оставить отзыв — напиши в поддержку: @AniAI_supportbot"
    )

    keyboard = [[InlineKeyboardButton("🚀 Начать работу", callback_data="go_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

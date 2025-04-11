import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from aiohttp import web

from ai.chat import handle_ask
from handlers.start import start
from handlers.menu import menu
import nest_asyncio

# Логи
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Создаём приложение
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("menu", menu))

# 🔧 Обработчик кнопок (вынесен отдельно — не внутри add_handler)
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_menu":
        text = (
            "🎉 Спасибо, что выбрал <b>AniAI</b> — интеллектуального ассистента, который поможет тебе в работе, учёбе и повседневной жизни!\n\n"
            "С AniAI ты получаешь быстрый и простой доступ к самым мощным нейросетям прямо в Telegram. "
            "Просто напиши свой запрос — и бот сам разберётся, что тебе нужно:\n\n"
            "<b>✨ Примеры запросов:</b>\n"
            "• Сгенерируй изображение города на Марсе в стиле киберпанк\n"
            "• Сделай краткое содержание документа (и прикрепи PDF или текст)\n"
            "• Напиши поздравление с днём рождения коллеге в шуточном стиле\n"
            "• Создай музыку в стиле lo-fi для работы\n"
            "• Переведи текст на английский\n\n"
            "<b>Что умеет AniAI:</b>\n"
            "1. 📘 Объясняет сложные темы простым языком\n"
            "2. ✍️ Помогает писать тексты, письма, описания\n"
            "3. 🌍 Переводит на любой язык\n"
            "4. 🖼 Генерирует иллюстрации и изображения\n"
            "5. 🎵 Пишет музыку под настроение\n"
            "6. 🎥 Создаёт короткие видео по сценарию\n"
            "7. 📄 Анализирует документы и выделяет главное\n"
            "8. 🔗 Ищет идеи, источники и вдохновение\n\n"
            "🤖 AniAI использует самые передовые модели — GPT-4o, Ideogram, Suno и другие. "
            "Первый доступ бесплатный в течение <b>50 дней</b>.\n\n"
            "💬 Если возникнут вопросы или хочешь оставить отзыв — напиши в поддержку: @AniAI_supportbot"
        )

        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=text,
            parse_mode="HTML"
        )

        # переход в меню
        await context.bot.send_message(chat_id=query.message.chat.id, text="/menu")

# 👇 Регистрация обработчика кнопок
app.add_handler(CallbackQueryHandler(handle_button))

# Webhook endpoint
async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

# Проверка сервера
async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")

# Основной запуск
async def main():
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()

    web_app = web.Application()
    web_app.router.add_post("/", handle_telegram)
    web_app.router.add_get("/", handle_check)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print(f"✅ AniAI слушает Webhook на {WEBHOOK_URL}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

import os
import logging
import asyncio
from dotenv import load_dotenv
from aiohttp import web
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import nest_asyncio

# Импорты обработчиков
from ai.chat import handle_ask
from handlers.start import start
from handlers.menu import menu, handle_button
from handlers.translate import translate
from handlers.image import generate_image
from handlers.analyze import analyze
from handlers.text import handle_text_message  # Универсальный обработчик текстов

# Логи
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

# Конфигурация
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Приложение Telegram
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(CommandHandler("image", generate_image))

# Обработчики интерактивных кнопок и документов
app.add_handler(CallbackQueryHandler(handle_button))
app.add_handler(MessageHandler(filters.Document.ALL, analyze))

# Универсальный обработчик текстовых сообщений
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

# Webhook-сервер
async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")

# Запуск приложения
async def main():
    await app.initialize()

    # Устанавливаем меню Telegram
    await app.bot.set_my_commands([
        BotCommand("menu", "📋 Главное меню AniAI"),
        BotCommand("ask", "🧠 Задать вопрос"),
        BotCommand("translate", "🌍 Перевести текст"),
        BotCommand("image", "🎨 Создать изображение"),
    ])

    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()

    # HTTP-сервер
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

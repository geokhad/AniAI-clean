
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")  # <-- уточни путь явно
import logging
import asyncio

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
from handlers.chat import handle_ask
from handlers.start import start
from handlers.menu import menu, handle_button
from handlers.translate import translate
from handlers.image import generate_image
from handlers.analyze import analyze
from handlers.text import handle_text_message
from handlers.voice import handle_voice_message  # ✅ Только голосовой ввод
from handlers.music import handle_music_prompt   # 🎼 Добавлен для генерации музыки

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
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("ask", handle_ask))            # GPT
app.add_handler(CommandHandler("translate", translate))       # Перевод
app.add_handler(CommandHandler("image", generate_image))      # Генерация изображений
app.add_handler(CommandHandler("music", handle_music_prompt)) # 🎼 Музыка по команде

# Обработчики кнопок и меню
app.add_handler(CallbackQueryHandler(handle_button))

# Обработчики сообщений
app.add_handler(MessageHandler(filters.Document.ALL, analyze))                             # 📎 Документы
app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))                      # 🎙 Голосовые
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))     # ✍️ Текстовые

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

    # Команды в Telegram
    await app.bot.set_my_commands([
    BotCommand("menu", "📋 Главное меню AniAI"),
    # BotCommand("music", "🎼 Сгенерировать музыку")  # ❌ Удалить или закомментировать
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

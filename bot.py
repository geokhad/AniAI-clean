import os
import logging
import asyncio
from dotenv import load_dotenv
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
import nest_asyncio

# Импорты команд
from ai.chat import handle_ask
from handlers.start import start
from handlers.menu import menu, handle_button
from handlers.translate import translate, handle_translation_text
from handlers.image import generate_image
from handlers.analyze import analyze

# Логи
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

app = ApplicationBuilder().token(TOKEN).build()

# Обработчики
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_translation_text))  # автообработка после /translate
app.add_handler(CommandHandler("image", generate_image))
app.add_handler(CallbackQueryHandler(handle_button))
app.add_handler(MessageHandler(filters.Document.ALL, analyze))

# Webhook сервер
async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

# Проверка доступности
async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")

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

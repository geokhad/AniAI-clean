import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from telegram import Update
from ai.chat import handle_ask
from handlers.start import start
from aiohttp import web
import nest_asyncio

# Настройка логов
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

# Telegram App
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

# Aiohttp сервер для Telegram Webhook

from telegram import Update

async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)  # превращаем JSON в Update
    await app.process_update(update)        # передаём в Telegram App
    return web.Response()


# Пинги на GET можно оставить
async def handle_check(request):
    return web.Response(text="✅ AniAI online")

# Запуск
async def main():
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()

    web_app = web.Application()
    web_app.add_routes([
        web.post("/", handle_telegram),
        web.get("/", handle_check),
    ])

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print(f"✅ AniAI слушает Webhook на {WEBHOOK_URL}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

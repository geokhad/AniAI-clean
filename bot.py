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

# Патч для nested loops
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

app = ApplicationBuilder().token(TOKEN).build()

# Регистрируем команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

# Aiohttp-приложение для Render
async def handle(request):
    return web.Response(text="AniAI online ✅")

web_app = web.Application()
web_app.add_routes([web.get("/", handle)])

async def main():
    print("🌐 Устанавливаем Webhook...")
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()
    print(f"✅ AniAI слушает Webhook на {WEBHOOK_URL}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

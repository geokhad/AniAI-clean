import os
import logging
from telegram.ext import ApplicationBuilder, CommandHandler
from ai.chat import handle_ask
from handlers.start import start
from dotenv import load_dotenv
import nest_asyncio

nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # добавь это в Render переменные

PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

print("✅ AniAI запущена через Webhook.")

async def main():
    await app.initialize()
    await app.start()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.updater.start_webhook(listen=HOST, port=PORT)
    await app.updater.idle()

import asyncio
asyncio.run(main())
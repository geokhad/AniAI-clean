import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

from handlers.start import start
from ai.chat import handle_ask
import nest_asyncio

# Настройка логов
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Функция запуска polling с удалением Webhook
async def main():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", handle_ask))

    print("🤖 AniAI запущена через polling.")
    await app.run_polling()

# Запуск
if __name__ == "__main__":
    asyncio.run(main())

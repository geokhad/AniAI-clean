import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from handlers.start import start
from ai.chat import handle_ask

# Настройки логов
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Загрузка переменных окружения
load_dotenv()

TOKEN = os.getenv("TOKEN")

# Удаляем Webhook, если он был установлен ранее
async def delete_webhook():
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)

asyncio.run(delete_webhook())

# Инициализация бота
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

# Запуск через polling
print("🤖 AniAI запущена через polling.")
app.run_polling()

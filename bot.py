import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from ai.chat import handle_ask
from handlers.start import start
import nest_asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Разрешаем вложенные asyncio петли (важно для Render и Jupyter)
nest_asyncio.apply()

# Загрузка переменных из .env или Render Environment
load_dotenv()

# Переменные окружения
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # например, https://aniai.onrender.com
PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

# Инициализация приложения
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

# Асинхронный запуск с Webhook
async def main():
    print("🌐 Настройка Webhook...")
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()
    print("✅ AniAI запущена через Webhook.")
    # Вебхук работает — ждем события
    await asyncio.Event().wait()  # бесконечное ожидание

# Запуск
if __name__ == "__main__":
    asyncio.run(main())

import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from ai.chat import handle_ask
from handlers.start import start
import nest_asyncio

# Настройка логов
logging.basicConfig(level=logging.INFO)

# Применение патча для Jupyter / Render
nest_asyncio.apply()

# Загрузка переменных окружения
load_dotenv()

# Чтение токена и адреса Webhook
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Например: https://aniai.onrender.com

# Конфигурация сервера
PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

# Инициализация приложения
app = ApplicationBuilder().token(TOKEN).build()

# Регистрируем команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

async def main():
    print("🌐 Настраиваем Webhook...")
    await app.initialize()
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()
    print("✅ AniAI запущена через Webhook.")
    await app.updater.start_polling()  # <- обязательно оставить, даже если не используется polling
    await app.updater.idle()

# Запускаем
if __name__ == "__main__":
    asyncio.run(main())


import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from aiohttp import web
from ai.chat import handle_ask
from handlers.start import start
from handlers.menu import menu
import nest_asyncio

# Логи
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()

# Обработчики команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("menu", menu))


# Обработка нажатий на кнопки
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "go_menu":
        await query.message.reply_text("📋 Главное меню AniAI загружается...")
        # создаем фейковый Update из CallbackQuery для команды menu
        fake_update = Update(update.update_id, message=query.message)
        await menu(fake_update, context)

    elif data == "ask":
        await query.message.reply_text("✍️ Напиши свой вопрос в формате: /ask Вопрос")

    elif data == "feedback":
        await query.message.reply_text("✍️ Напиши отзыв в формате: /feedback Текст отзыва")

    elif data == "launch":
        await query.message.reply_text("🚀 AniAI запущена. Просто напиши, что тебе нужно!")

    elif data == "help":
        await query.message.reply_text("ℹ️ Список команд:\n/start\n/ask\n/menu\n/feedback")


app.add_handler(CallbackQueryHandler(handle_button))


# aiohttp веб-сервер для Webhook
async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

# Проверка доступности
async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")


# Основной запуск
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

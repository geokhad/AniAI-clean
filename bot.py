import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
)
from aiohttp import web
import nest_asyncio

from ai.chat import handle_ask
from handlers.start import start
from handlers.menu import menu

# Логи
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Приложение Telegram
app = ApplicationBuilder().token(TOKEN).build()

# Команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("menu", menu))

# Обработка кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_menu":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📋 Главное меню AniAI загружается..."
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text="/menu")

    elif query.data == "gpt_help":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🧠 GPT-помощь доступна. Просто напиши:\n\n"
                 "• Объясни это простыми словами...\n"
                 "• Составь план статьи о...\n"
                 "• Сформулируй тезисы из текста...\n"
                 "• Переведи этот текст на английский...",
        )

    elif query.data == "voice_mode":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🎙 Режим голосовых пока в разработке, но скоро появится. Следите за обновлениями!"
        )

    elif query.data == "switch_language":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🌐 Пока доступен только русский язык. В будущем — автоматическое определение и переключение 🇷🇺/🇬🇧"
        )

    elif query.data == "premium_mode":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="💳 Премиум-режим будет доступен после 50 бесплатных дней.\n"
                 "Здесь появятся плюшки, приоритет, больше лимитов и доступ к GPT-4o 🔓"
        )

    elif query.data == "feedback":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="✍️ Напиши свой отзыв в формате:\n\n/feedback Мне очень понравилось, спасибо!"
        )

app.add_handler(CallbackQueryHandler(handle_button))

# Aiohttp Webhook
async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")

# Запуск
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

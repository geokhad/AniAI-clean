
import os
import logging
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from aiohttp import web
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Загрузка переменных окружения
load_dotenv(dotenv_path=".env")

# Импорт обработчиков
from handlers.start import start
from handlers.menu import menu, handle_button
from handlers.chat import handle_ask
from handlers.translate import translate
from handlers.image import generate_image
from handlers.analyze import analyze
from handlers.text import handle_text_message
from handlers.voice import handle_voice_message
from handlers.music import handle_music_prompt
from handlers.daily_english import handle_daily_answer
from handlers.spaced_repetition import start_spaced_vocab
from handlers.exam_mode import start_voa_exam, handle_voa_text_exam, handle_voa_voice_exam

# Логирование
logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()

# Конфигурация
TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

# Создание приложения
app = ApplicationBuilder().token(TOKEN).build()

# Команды
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("menu", menu))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("translate", translate))
app.add_handler(CommandHandler("image", generate_image))
app.add_handler(CommandHandler("music", handle_music_prompt))
app.add_handler(CommandHandler("spaced", start_spaced_vocab))

# Callback-кнопки
app.add_handler(CallbackQueryHandler(handle_daily_answer, pattern="^daily_answer"))  # ✅ Сначала фильтрованные
app.add_handler(CallbackQueryHandler(handle_button))  # ✅ Потом общее меню

# Обработка сообщений
app.add_handler(MessageHandler(filters.Document.ALL, analyze))
app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

# Обработка режима VOA Exam
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_voa_text_exam))
app.add_handler(MessageHandler(filters.VOICE, handle_voa_voice_exam))

# Webhook хендлер
async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

# Тестовая страница
async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")

# Главный запуск
async def main():
    await app.initialize()

    await app.bot.set_my_commands([
        BotCommand("menu", "📋 Главное меню AniAI"),
        BotCommand("spaced", "🎧 Интервальное повторение")
    ])

    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.start()

    # HTTP-сервер
    web_app = web.Application()
    web_app.router.add_post("/", handle_telegram)
    web_app.router.add_get("/", handle_check)

    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    print(f"✅ AniAI listening at {WEBHOOK_URL}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())

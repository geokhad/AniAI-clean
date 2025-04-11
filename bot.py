import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from aiohttp import web
from ai.chat import handle_ask
from handlers.start import start
from handlers.menu import menu
import nest_asyncio

logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.environ.get("PORT", 8080))
HOST = "0.0.0.0"

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))
app.add_handler(CommandHandler("menu", menu))

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "go_menu":
        await context.bot.send_message(chat_id=query.message.chat.id, text="📋 Главное меню AniAI загружается...")
        await menu(update, context)
    elif query.data == "gpt_help":
        await query.message.reply_text("🧠 Напиши /ask и свой вопрос для GPT-помощи.")
    elif query.data == "voice_mode":
        await query.message.reply_text("🎙 Голосовой режим будет доступен в будущих обновлениях.")
    elif query.data == "change_lang":
        await query.message.reply_text("🌐 Поддержка языков в разработке.")
    elif query.data == "premium":
        await query.message.reply_text("💎 Премиум режим: первые 50 дней бесплатно!")
    elif query.data == "feedback":
        await query.message.reply_text("✍️ Напиши отзыв в формате: 'Отзыв: ...' и мы обязательно его учтём.")

app.add_handler(CallbackQueryHandler(handle_button))

async def handle_telegram(request):
    data = await request.json()
    update = Update.de_json(data, app.bot)
    await app.process_update(update)
    return web.Response(text="OK")

async def handle_check(request):
    return web.Response(text="AniAI on Railway ✅")

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

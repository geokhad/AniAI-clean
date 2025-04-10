import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler
from ai.chat import handle_ask
from handlers.start import start
import nest_asyncio

logging.basicConfig(level=logging.INFO)
nest_asyncio.apply()
load_dotenv()

TOKEN = os.getenv("TOKEN")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

print("✅ AniAI запущена через polling.")

if __name__ == "__main__":
    import asyncio

    async def run():
        # Удаляет Webhook, если был установлен — чтобы не было конфликтов
        await app.bot.delete_webhook(drop_pending_updates=True)

        # Запускает бота в режиме polling
        await app.run_polling()

    asyncio.run(run())


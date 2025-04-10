from dotenv import load_dotenv
load_dotenv()
from ai.chat import handle_ask
from handlers.start import start
from telegram.ext import ApplicationBuilder, CommandHandler

import os
import nest_asyncio
nest_asyncio.apply()

TOKEN = os.environ["TOKEN"]
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", handle_ask))

print("✅ AniAI запущена")
app.run_polling()

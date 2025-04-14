# handlers/start.py

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.google_sheets import log_subscriber

# 👋 Стартовое приветствие и кнопка
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_subscriber(user.id, user.full_name, user.username)

    text = """👋 <b>Добро пожаловать в <u>AniAI</u></b> — твою умную помощницу на базе нейросетей!

✨ Делай то, что хочешь, когда хочешь и так долго, как хочешь.

• 💬 Общайся с ИИ: задавай вопросы, получай советы, пиши тексты  
• 🖼 Генерируй изображения по описанию  
• 🎶 Получай музыку под настроение  
• 🎙 Говори голосом — и я всё пойму  
• 📄 Отправляй документы на анализ  

И всё это — прямо в Telegram!  
🚀 Готова начать? Жми на кнопку ниже 👇
"""

    keyboard = [[InlineKeyboardButton("🚀 Начать работу", callback_data="go_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from utils.google_sheets import log_subscriber

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_subscriber(user.id, user.full_name, user.username)

    text = """👋 <b>Добро пожаловать в <u>AniAI</u></b> — вашего умного помощника на базе нейросетей!

✨ Используй возможности ИИ без сложных настроек и VPN — просто открой бот и начни:

• 💬 Общайся с нейросетью: задавай вопросы, проси советы, создавай тексты  
• 🖼 Генерируй изображения по описанию  
• 🎶 Получай музыку и мелодии под настроение  
• 🎬 Проси видео и визуальный контент — AniAI справится!

И это лишь начало — бот умеет куда больше, чем ты думаешь.  
🚀 Готов начать? Нажми кнопку ниже 👇
"""

    keyboard = [[InlineKeyboardButton("🚀 Начать работу", callback_data="go_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.google_sheets import log_subscriber

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    log_subscriber(user.id, user.full_name, user.username)

    text = (
        "👋 Добро пожаловать в <b>AniAI</b> — вашего умного помощника на базе нейросетей!\n\n"
        "✨ Используй все возможности ИИ без сложных настроек и VPN — просто открой бот и начни:\n\n"
        "• 💬 Общайся с нейросетью: задавай вопросы, проси советы, создавай тексты\n"
        "• 🖼 Генерируй изображения по описанию\n"
        "• 🎶 Получай музыку и мелодии под настроение\n"
        "• 🎥 Проси видео и визуальный контент — AniAI справится!\n\n"
        "И это лишь начало — бот умеет куда больше, чем ты думаешь.\n\n"
        "🚀 Готов начать? Нажми кнопку ниже 👇"
    )

    keyboard = [
        [InlineKeyboardButton("🚀 Начать работу", callback_data="go_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

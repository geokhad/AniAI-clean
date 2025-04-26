
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.state import (
    active_ask,
    active_translators,
    active_imagers,
    active_analyzers,
    clear_user_state,
    active_tts
)
from handlers.daily_english import start_daily_english
from handlers.exam_mode import start_voa_exam  # ✅ Актуальный импорт

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🧠 Вопрос", callback_data="gpt_help"),
            InlineKeyboardButton("🎨 Картинка", callback_data="image_help")
        ],
        [
            InlineKeyboardButton("🎼 Музыка", callback_data="music_help"),
            InlineKeyboardButton("🎬 Видео", callback_data="video_help")
        ],
        [
            InlineKeyboardButton("📄 Документ", callback_data="analyze_help"),
            InlineKeyboardButton("🌍 Перевод", callback_data="translate")
        ],
        [
            InlineKeyboardButton("🎙 Голос", callback_data="voice_mode"),
            InlineKeyboardButton("🗣 Озвучка", callback_data="tts_mode")
        ],
        [
            InlineKeyboardButton("📝 Daily English", callback_data="daily_english"),
            InlineKeyboardButton("🧠 VOA exam", callback_data="voa_vocab")
        ],
        [
            InlineKeyboardButton("💎 Премиум", callback_data="premium_mode"),
            InlineKeyboardButton("🤝 Партнёрка", callback_data="affiliate")
        ],
        [
            InlineKeyboardButton("✍️ Отзыв", callback_data="feedback")
        ]
    ]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="📋 Главное меню AniAI:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data in ["go_menu", "voice_mode", "tts_mode", "change_language", "premium_mode", "feedback"]:
        clear_user_state(user_id)

    if query.data == "go_menu":
        await menu(update, context)
        return

    if query.data == "gpt_help":
        active_ask.add(user_id)
        await context.bot.send_message(chat_id=query.message.chat.id, text="🧠 Просто задай вопрос...")
        return

    if query.data == "image_help":
        active_imagers.add(user_id)
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎨 Опиши изображение...")
        return

    if query.data == "music_help":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎼 Генерация музыки в разработке.")
        return

    if query.data == "video_help":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎬 Генерация видео в разработке.")
        return

    if query.data == "analyze_help":
        active_analyzers.add(user_id)
        await context.bot.send_message(chat_id=query.message.chat.id, text="📄 Прикрепи документ для анализа.")
        return

    if query.data == "translate":
        active_translators.add(user_id)
        await context.bot.send_message(chat_id=query.message.chat.id, text="🌍 Введи текст для перевода.")
        return

    if query.data == "tts_mode":
        active_tts.add(user_id)
        await context.bot.send_message(chat_id=query.message.chat.id, text="🗣 Введи текст для озвучки.")
        return

    if query.data == "voice_mode":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎙 Отправь голосовое сообщение...")
        return

    if query.data == "daily_english":
        await start_daily_english(update, context)
        return

    if query.data == "voa_vocab":
        await start_voa_exam(update, context)  # ✅ Подключён новый модуль по правилам
        return

    if query.data == "affiliate":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🤝 Партнёрская программа...")
        return

    responses = {
        "change_language": "🌐 Язык будет доступен позже.",
        "premium_mode": "💎 Премиум режим скоро появится.",
        "feedback": "✍️ Напиши отзыв: @AniAI_supportbot"
    }

    response = responses.get(query.data)
    if response:
        await context.bot.send_message(chat_id=query.message.chat.id, text=response)
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Функция в разработке.")

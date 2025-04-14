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

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🧠 Задать вопрос", callback_data="gpt_help")],
        [InlineKeyboardButton("📸 Сгенерировать изображение", callback_data="image_help")],
        [InlineKeyboardButton("📄 Проанализировать документ", callback_data="analyze_help")],
        [InlineKeyboardButton("🌍 Перевести текст", callback_data="translate")],
        [InlineKeyboardButton("🎙 Голосовой ввод", callback_data="voice_mode")],
        [InlineKeyboardButton("🗣 Озвучить текст", callback_data="tts_mode")],
        [InlineKeyboardButton("🌐 Переключить язык (временно недоступно)", callback_data="change_language")],
        [InlineKeyboardButton("💎 Премиум режим", callback_data="premium_mode")],
        [InlineKeyboardButton("🤝 Партнёрская программа", callback_data="affiliate")],
        [InlineKeyboardButton("✍️ Оставить отзыв", callback_data="feedback")],
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
        intro = (
            "👋 Рада тебя видеть! Я — AniAI, твоя помощница на базе нейросетей.\n\n"
            "✨ Делай то, что хочешь, когда хочешь и так долго, как хочешь.\n\n"
            "Вот что я умею:\n"
            "• 🧠 Отвечаю на вопросы и объясняю сложное простыми словами\n"
            "• 📸 Генерирую картинки по твоему описанию\n"
            "• 🌍 Перевожу тексты и распознаю языки\n"
            "• 🎧 Озвучиваю текст женским голосом\n"
            "• 📄 Обрабатываю и пересказываю документы\n\n"
            "И всё это — прямо в Telegram!\n"
            "👇 Выбери, с чего хочешь начать:"
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text=intro)
        await menu(update, context)
        return

    if query.data == "gpt_help":
        active_ask.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🧠 Просто задай вопрос, и я постараюсь объяснить всё ясно и по делу. Например: «Объясни квантовую запутанность простыми словами»"
        )
        return

    if query.data == "image_help":
        active_imagers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📸 Опиши, что ты хочешь увидеть. Например: «город на облаках в стиле стимпанк»"
        )
        return

    if query.data == "analyze_help":
        active_analyzers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📄 Прикрепи документ (PDF, DOCX, TXT) — и я сделаю краткий пересказ или анализ."
        )
        return

    if query.data == "translate":
        active_translators.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🌍 Введи текст — я переведу его на нужный язык."
        )
        return

    if query.data == "tts_mode":
        active_tts.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🗣 Введи фразу — я озвучу её своим голосом."
        )
        return

    if query.data == "voice_mode":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=(
                "🎙 <b>Голосовой режим AniAI</b>\n\n"
                "Просто отправь голосовое сообщение — я распознаю текст и пойму, что ты хочешь 🤖\n\n"
                "✨ Ты можешь:\n"
                "• Сказать: «переведи на английский язык я тебя люблю» — и я переведу\n"
                "• Сказать: «сгенерируй картинку с котом» — и я её создам\n"
                "• Продиктовать текст — я предложу перевод, если язык другой\n"
                "• Задать вопрос — и я включу режим ответа\n\n"
                "💡 Говори со мной свободно — я подстроюсь под тебя 🪄"
            ),
            parse_mode="HTML"
        )
        return

    if query.data == "affiliate":
        text = (
            "🤝 <b>Партнёрская программа AniAI</b>\n\n"
            "Приглашай пользователей — получай % от всех их покупок в течение 1 месяца.\n\n"
            "📌 Твоя реферальная ссылка:\n"
            "<code>https://t.me/AniAI_newbot?start=ref</code>\n\n"
            "Чем больше людей — тем больше твой доход 💸"
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode="HTML")
        return

    responses = {
        "change_language": "🌐 Переключение языка будет доступно в следующем обновлении.",
        "premium_mode": "💎 Премиум-режим включает GPT-4 и расширенные лимиты. Скоро будет доступен.",
        "feedback": "📬 Напиши своё мнение или пожелание: @AniAI_supportbot"
    }

    response = responses.get(query.data)
    if response:
        await context.bot.send_message(chat_id=query.message.chat.id, text=response, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Эта функция пока в разработке.")

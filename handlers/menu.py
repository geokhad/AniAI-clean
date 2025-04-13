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
        [InlineKeyboardButton("🧠 GPT-помощь", callback_data="gpt_help")],
        [InlineKeyboardButton("📸 Сгенерировать изображение", callback_data="image_help")],
        [InlineKeyboardButton("📄 Проанализировать документ", callback_data="analyze_help")],
        [InlineKeyboardButton("🌍 Перевести текст", callback_data="translate")],
        [InlineKeyboardButton("🎙 Голосовой ввод", callback_data="voice_mode")],
        [InlineKeyboardButton("🗣 Озвучить текст", callback_data="tts_mode")],
        [InlineKeyboardButton("ℹ️ Голосовые команды", callback_data="voice_help")],
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
            "🎉 Спасибо, что выбрал AniAI — интеллектуального ассистента, который поможет тебе в работе, учёбе и повседневной жизни!\n\n"
            "С AniAI ты получаешь быстрый и простой доступ к самым мощным нейросетям прямо в Telegram. Просто напиши свой запрос — и бот сам разберётся, что тебе нужно:\n\n"
            "✨ Примеры:\n"
            "• Сгенерируй изображение города на Марсе в стиле киберпанк\n"
            "• Сделай краткое содержание документа (и прикрепи PDF или текст)\n"
            "• Напиши поздравление коллеге\n"
            "• Создай музыку в стиле lo-fi\n"
            "• Переведи текст на английский\n\n"
            "🤖 AniAI использует модели GPT-4o, DALL·E, Suno и другие.\n"
            "📆 Бесплатный доступ — 50 дней!\n\n"
            "👇 Главное меню:"
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text=intro)
        await menu(update, context)
        return

    if query.data == "gpt_help":
        active_ask.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🧠 Просто задай вопрос, и AniAI ответит. Например: «Объясни квантовую запутанность простыми словами»"
        )
        return

    if query.data == "image_help":
        active_imagers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📸 Опиши, что нужно изобразить."
        )
        return

    if query.data == "analyze_help":
        active_analyzers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📄 Прикрепи документ (PDF, DOCX, TXT) — и я сделаю краткое резюме."
        )
        return

    if query.data == "translate":
        active_translators.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🌍 Введи текст для перевода."
        )
        return

    if query.data == "tts_mode":
        active_tts.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🗣 Введи текст, который нужно озвучить. Я превращу его в голосовое сообщение."
        )
        return

    if query.data == "affiliate":
        text = (
            "🤝 <b>Партнёрская программа AniAI</b>\n\n"
            "Приглашай пользователей — получай % от всех их покупок в течение 1 месяца.\n\n"
            "📌 Твоя реферальная ссылка:\n"
            "<code>https://t.me/AniAI_newbot?start=ref</code>\n\n"
            "Чем больше пользователей перейдёт — тем выше твой доход 💸"
        )
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode="HTML")
        return

    responses = {
        "voice_mode": (
            "🎙 <b>Голосовой режим AniAI</b>\n\n"
            "Просто отправь голосовое сообщение — я его расшифрую с помощью Whisper.\n\n"
            "🗣 И ты можешь говорить команды:\n"
            "• «Переведи это»\n"
            "• «Сгенерируй картинку»\n"
            "• «Озвучь текст»\n"
            "• «Объясни что такое...»\n\n"
            "Я сам определю, какой режим включить 🤖"
        ),
        "voice_help": (
            "🗣 <b>Поддерживаемые голосовые команды</b>\n\n"
            "Ты можешь просто сказать:\n"
            "• «Переведи это» — включится режим перевода\n"
            "• «Сгенерируй картинку» — генерация изображения\n"
            "• «Озвучь текст» — включится озвучка\n"
            "• «Объясни...», «Что такое...» — включается GPT-помощь\n\n"
            "Попробуй говорить так, как пишешь — я всё пойму 🤖"
        ),
        "change_language": "🌐 Переключение языка будет доступно в следующем обновлении.",
        "premium_mode": "💎 Премиум-режим включает GPT-4 и расширенные лимиты. Скоро будет доступен.",
        "feedback": "📬 Оставьте отзыв или пожелание здесь: @AniAI_supportbot"
    }

    response = responses.get(query.data)
    if response:
        await context.bot.send_message(chat_id=query.message.chat.id, text=response, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Функция в разработке.")

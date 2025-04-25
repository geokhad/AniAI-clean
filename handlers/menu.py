from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers.state import (
    active_ask,
    active_translators,
    active_imagers,
    active_analyzers,
    clear_user_state,
    active_tts,
)
from handlers.daily_english import start_daily_english
from handlers.spaced_repetition import start_spaced_vocab  # ✅ Добавлено

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
            InlineKeyboardButton("🧠 VOA exam", callback_data="spaced_vocab")  # ✅ Добавлено
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

    if query.data in [
        "go_menu", "voice_mode", "tts_mode", "change_language", "premium_mode", "feedback"
    ]:
        clear_user_state(user_id)

    if query.data == "go_menu":
        intro = """👋 Рада тебя видеть! Я — AniAI, твоя помощница на базе нейросетей.

✨ Делай то, что хочешь, когда хочешь и так долго, как хочешь.

Вот что я умею:
• 🧠 Отвечаю на вопросы и объясняю сложное простыми словами
• 🎨 Генерирую картинки по твоему описанию
• 🎼 Создаю музыку по твоим ощущениям
• 🎬 В перспективе — генерирую видео
• 🌍 Перевожу тексты и распознаю языки
• 🎧 Озвучиваю текст женским голосом
• 📄 Обрабатываю и пересказываю документы
• 🧠 Помогаю учить английский с голосом и повторением

👇 Выбери, с чего хочешь начать:"""
        await context.bot.send_message(chat_id=query.message.chat.id, text=intro)
        await menu(update, context)
        return

    if query.data == "gpt_help":
        active_ask.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🧠 Просто задай вопрос, и я постараюсь объяснить всё ясно и по делу."
        )
        return

    if query.data == "image_help":
        active_imagers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🎨 Опиши, что ты хочешь увидеть. Например: «город на облаках в стиле стимпанк»"
        )
        return

    if query.data == "music_help":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎼 Функция генерации музыки сейчас в разработке.")
        return

    if query.data == "video_help":
        await context.bot.send_message(chat_id=query.message.chat.id, text="🎬 Функция генерации видео сейчас в разработке.")
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
            text="🎙 Просто отправь голосовое сообщение, и я пойму, что ты хочешь 🤖"
        )
        return

    if query.data == "daily_english":
        await start_daily_english(update, context)
        return

    if query.data == "spaced_vocab":
        await start_spaced_vocab(update, context)
        return

    if query.data == "affiliate":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🤝 Приглашай друзей и получай бонусы! Подробности — @AniAI_supportbot"
        )
        return

    responses = {
        "change_language": "🌐 Переключение языка будет доступно в следующем обновлении.",
        "premium_mode": "💎 Премиум режим скоро появится!",
        "feedback": "📬 Напиши своё мнение или пожелание: @AniAI_supportbot"
    }

    if query.data in responses:
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text=responses[query.data]
        )

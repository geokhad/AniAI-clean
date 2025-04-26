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
from handlers.exam_mode import start_voa_exam

# Главное меню
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

# Обработка нажатий кнопок
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Если переход в режим — сброс активностей
    if query.data in ["go_menu", "voice_mode", "tts_mode", "change_language", "premium_mode", "feedback"]:
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

И всё это — прямо в Telegram!
👇 Выбери, с чего хочешь начать:"""
        await context.bot.send_message(chat_id=query.message.chat.id, text=intro)
        await menu(update, context)
        return

    # Обработка конкретных функций
    if query.data == "gpt_help":
        active_ask.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🧠 Просто задай вопрос — я объясню простыми словами! Например: «Что такое квантовая запутанность?»"
        )
        return

    if query.data == "image_help":
        active_imagers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🎨 Опиши картинку, которую хочешь получить. Например: «замок в облаках в стиле фэнтези»"
        )
        return

    if query.data == "music_help":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🎼 Генерация музыки скоро будет доступна. Следи за обновлениями!"
        )
        return

    if query.data == "video_help":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="🎬 Генерация видео в разработке. Скоро запустим!"
        )
        return

    if query.data == "analyze_help":
        active_analyzers.add(user_id)
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="📄 Прикрепи документ (PDF, DOCX, TXT), я помогу сделать пересказ или анализ."
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
            text="🗣 Введи текст — я озвучу его красивым голосом!"
        )
        return

    if query.data == "voice_mode":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="""🎙 <b>Голосовой режим AniAI</b>

Просто отправь голосовое сообщение — я распознаю текст и выполню команду.

✨ Возможности:
• Перевод: «переведи на английский я тебя люблю»
• Генерация: «создай картинку закат над океаном»
• Музыка: «сыграй утреннюю мелодию»
• Вопросы: «объясни, что такое блокчейн»
• Озвучка: «озвучь текст доброе утро»

💡 Говори свободно — я всё пойму!""", parse_mode="HTML"
        )
        return

    if query.data == "daily_english":
        await start_daily_english(update, context)
        return

    if query.data == "daily_next":
        await start_daily_english(update, context)
        return

    if query.data == "voa_vocab":
        await start_voa_exam(update, context)
        return

    if query.data == "affiliate":
        await context.bot.send_message(
            chat_id=query.message.chat.id,
            text="""🤝 <b>Партнёрская программа AniAI</b>

Приглашай друзей — получай бонусы от их покупок 30 дней подряд!

📌 Твоя ссылка:
<code>https://t.me/AniAI_newbot?start=ref</code>""",
            parse_mode="HTML"
        )
        return

    # Статические ответы
    responses = {
        "change_language": "🌐 Переключение языка будет доступно в следующем обновлении.",
        "premium_mode": """💎 <b>Премиум режим AniAI</b>

Доступно:
• GPT-4 ответы
• Расширенные лимиты
• 📌 Память последних сообщений (5 реплик)

Скоро запуск премиум-подписки!""",
        "feedback": "📬 Хочешь оставить отзыв или предложение? Пиши в поддержку: @AniAI_supportbot"
    }

    if query.data in responses:
        await context.bot.send_message(chat_id=query.message.chat.id, text=responses[query.data], parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Эта функция пока недоступна.")


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
        [
            InlineKeyboardButton(" 🧠 Вопрос", callback_data="gpt_help"),
            InlineKeyboardButton(" 🎨 Картинка", callback_data="image_help")
        ],
        [
            InlineKeyboardButton(" 🎼 Музыка", callback_data="music_help"),
            InlineKeyboardButton(" 🎬 Видео", callback_data="video_help")
        ],
        [
            InlineKeyboardButton(" 📄 Документ", callback_data="analyze_help"),
            InlineKeyboardButton(" 🌍 Перевод", callback_data="translate")
        ],
        [
            InlineKeyboardButton(" 🎙 Голос", callback_data="voice_mode"),
            InlineKeyboardButton(" 🗣 Озвучка", callback_data="tts_mode")
        ],
        [
            InlineKeyboardButton(" 💎 Премиум", callback_data="premium_mode"),
            InlineKeyboardButton(" 🤝 Партнёрка", callback_data="affiliate")
        ],
        [
            InlineKeyboardButton(" ✍️ Отзыв", callback_data="feedback")
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
            text="""🎙 <b>Голосовой режим AniAI</b>

Просто отправь голосовое сообщение — я распознаю текст и пойму, что ты хочешь 🤖

✨ Ты можешь:
• Сказать: «переведи на английский язык я тебя люблю» — и я переведу
• Сказать: «сгенерируй картинку с котом» — и я её создам
• Сказать: «сыграй мелодию для спокойного утра» — и я сгенерирую музыку
• Продиктовать текст — я предложу перевод, если язык другой
• Задать вопрос — и я включу режим ответа

💡 Говори со мной свободно — я подстроюсь под тебя 🪄""", parse_mode="HTML"
        )
        return

    if query.data == "affiliate":
        text = """🤝 <b>Партнёрская программа AniAI</b>

Приглашай пользователей — получай % от всех их покупок в течение 1 месяца.

📌 Твоя реферальная ссылка:
<code>https://t.me/AniAI_newbot?start=ref</code>

Чем больше людей — тем больше твой доход 💸"""
        await context.bot.send_message(chat_id=query.message.chat.id, text=text, parse_mode="HTML")
        return

    responses = {
        "change_language": "🌐 Переключение языка будет доступно в следующем обновлении.",
        "premium_mode": """💎 <b>Премиум режим AniAI</b>

Доступные функции:
• GPT-4 для более точных и развёрнутых ответов
• Расширенные лимиты на запросы и длину сообщений
• 📌 Новое: <b>Контекстный диалог</b> — память последних 5 реплик и автоочистка через 10 минут.

⚙️ Эта функция будет доступна в ближайшем обновлении для премиум-пользователей.""",
        "feedback": "📬 Напиши своё мнение или пожелание: @AniAI_supportbot"
    }

    response = responses.get(query.data)
    if response:
        await context.bot.send_message(chat_id=query.message.chat.id, text=response, parse_mode="HTML")
    else:
        await context.bot.send_message(chat_id=query.message.chat.id, text="⚙️ Эта функция пока в разработке.")

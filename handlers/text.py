from telegram import Update
from telegram.ext import ContextTypes

from handlers.state import (
    active_translators,
    active_imagers,
    active_ask,
    active_tts,
    active_music  # ✅ Добавлено
)

from handlers.translate import handle_translation_text
from handlers.image import handle_image_prompt
from handlers.chat import handle_gpt_text
from handlers.voice import handle_tts_text
from handlers.music import handle_music_prompt  # ✅ Добавлено

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # ✅ Проверка: есть ли текст вообще
    if not update.message or not update.message.text:
        return

    # 📝 Логируем входящие сообщения
    print(f"[Text] Сообщение от {user_id}: {update.message.text}")

    # 🔁 Приоритет: перевод > изображение > озвучка > музыка > GPT
    if user_id in active_translators:
        await handle_translation_text(update, context)
        return

    if user_id in active_imagers:
        await handle_image_prompt(update, context)
        return

    if user_id in active_tts:
        await handle_tts_text(update, context)
        return

    if user_id in active_music:
        await handle_music_prompt(update, context)
        active_music.discard(user_id)
        return

    if user_id in active_ask:
        await handle_gpt_text(update, context)
        return

    # 🧩 Если ни один режим не активен
    await update.message.reply_text(
        "🤖 Я пока не понимаю, что делать с этим сообщением.\n"
        "Пожалуйста, выбери режим в меню или задай голосовую команду."
    )

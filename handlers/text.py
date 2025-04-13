from telegram import Update
from telegram.ext import ContextTypes

from handlers.state import active_translators, active_imagers, active_ask  # 🔄 Исправлено имя
from handlers.translate import handle_translation_text
from handlers.image import handle_image_prompt
from handlers.chat import handle_gpt_text

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # 🔁 Приоритет: перевод > изображение > GPT
    if user_id in active_translators:
        await handle_translation_text(update, context)
        return

    if user_id in active_imagers:  # 🔄 Исправлено имя
        await handle_image_prompt(update, context)
        return

    if user_id in active_ask:
        await handle_gpt_text(update, context)
        return

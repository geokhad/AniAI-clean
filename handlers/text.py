from telegram import Update
from telegram.ext import ContextTypes

from handlers.translate import active_translators, handle_translation_text
from handlers.image import active_image, handle_image_prompt

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Приоритет: сначала перевод, потом изображение
    if user_id in active_translators:
        await handle_translation_text(update, context)
    elif user_id in active_image:
        await handle_image_prompt(update, context)

from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("❗ Пожалуйста, укажи описание после команды /image.")
        return

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response.data[0].url
        await update.message.reply_photo(photo=image_url, caption="🖼 Вот изображение по твоему запросу!")
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при генерации изображения: {e}")


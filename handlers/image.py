from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_imagers

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ✅ Активация режима генерации изображений
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_imagers.add(user_id)
    await update.message.reply_text("📸 Опиши, что нужно изобразить.")

# ✅ Обработка текстового запроса
async def handle_image_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in active_imagers:
        return

    prompt = update.message.text.strip()
    if not prompt:
        await update.message.reply_text("❗ Пожалуйста, укажи, что нужно сгенерировать.")
        return

    await create_image(update, prompt)

# ✅ Генерация изображения с обработкой ошибок
async def create_image(update: Update, prompt: str):
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
        if "content_policy_violation" in str(e):
            await update.message.reply_text("🚫 Извините, этот запрос нарушает политику безопасности и не может быть выполнен.")
        else:
            await update.message.reply_text(f"⚠️ Ошибка при генерации изображения: {e}")

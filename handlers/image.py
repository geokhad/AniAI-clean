from telegram import Update
from telegram.ext import ContextTypes
import os
from openai import OpenAI
from handlers.state import active_imagers

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 🔒 Фильтр запрещённых слов
BANNED_WORDS = [
    "порно", "секс", "убийство", "насилие", "террор", "украин", "хохол", "русня",
    "москаль", "бандера", "взрыв", "бомба", "атака", "нах", "еба", "пизд", "сука", "хуй",
    "бляд", "жопа", "fuck", "shit", "asshole", "terror", "kill", "rape"
]

def contains_banned_words(text: str) -> bool:
    lower = text.lower()
    return any(bad in lower for bad in BANNED_WORDS)

# ✅ Активация режима генерации изображений вручную
async def generate_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_imagers.add(user_id)
    await update.message.reply_text("📸 Включён режим генерации. Опиши, что нужно сгенерировать.")

# ✅ Обработка текстового или переданного запроса
async def handle_image_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, prompt: str = None):
    user_id = update.effective_user.id

    # если prompt пришёл (например, из voice.py) — генерируем сразу
    if prompt:
        if contains_banned_words(prompt):
            await update.message.reply_text("🚫 Запрос содержит запрещённые слова и не может быть обработан.")
            return
        await update.message.reply_text("🤖 Думаю над изображением…")
        await create_image(update, prompt)
        return

    # если пользователь активировал режим, ждём текст
    if user_id not in active_imagers:
        return

    prompt = update.message.text.strip()
    if not prompt:
        await update.message.reply_text("❗ Пожалуйста, укажи, что нужно сгенерировать.")
        return

    if contains_banned_words(prompt):
        await update.message.reply_text("🚫 Запрос содержит запрещённые слова и не может быть обработан.")
        return

    await update.message.reply_text("🤖 Думаю над изображением…")
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

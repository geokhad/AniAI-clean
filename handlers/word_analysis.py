import openai
from telegram import Update
from telegram.ext import ContextTypes
from utils.google_sheets import append_to_sheet
from utils.voice_tools import synthesize_and_send
from datetime import datetime  # ✅ Добавлено

# Holla English промпт
HOLLA_PROMPT = """
Ты американец-носитель с 20-летним опытом преподавания английского. Объясни слово по методике Holla English.

Слово: "{word}"

Следуй чёткой структуре (13 пунктов), как в образце. Объясняй просто, естественно и с примерами из повседневной жизни.

Объяснение на русском. Все примеры — короткие и реалистичные. Озвучку делаем только для английского слова и 3–4 лучших примеров.
"""

# Основная функция
async def handle_word_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📘 Разбираю слово *{word}*...",
        parse_mode="Markdown"
    )

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": HOLLA_PROMPT.format(word=word)
            }],
            temperature=0.5
        )
        result = response.choices[0].message.content

        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=result
        )

        await synthesize_and_send(
            text=word,
            chat_id=update.effective_chat.id,
            context=context
        )

        # ✅ Добавлено логирование с датой и временем
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        append_to_sheet("Word_Analysis", [[str(user_id), word, now]])

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ошибка при разборе слова. Попробуй другое или повтори позже."
        )
        print("Word analysis error:", e)

import os
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from utils.google_sheets import append_to_sheet
from utils.voice_tools import synthesize_and_send
from openai import AsyncOpenAI

# Создаём OpenAI-клиент один раз
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Полный промпт Holla English с 13 шагами
HOLLA_PROMPT = """
Ты американец-носитель с 20-летним опытом преподавания английского. У тебя сертификаты CELTA, TOEFL, IELTS — сданы на максимальные баллы. Ты объясняешь английские слова так, чтобы русскоязычные ученики могли легко понять, запомнить и начать применять слово в реальной жизни, особенно в современной американской культуре.

Разбери слово: "{word}"

Используй строго следующий формат ответа с 13 пунктами:

1. Простое определение слова (на русском) — 1–2 ключевых значения. Если это глагол, добавь *to*.

2. Ближайшие аналоги в русском — с пояснением по контексту (например: "решить проблему", "обратиться к кому-то").

3. Применимость — когда и зачем используют это слово. Укажи 3–5 ситуаций в формате: короткое описание + пример на английском.

4. Когда НЕ стоит использовать — укажи ❌ типичные ошибки и путаницу со схожими словами.

5. Типичные ошибки не-носителей — тоже с ❌ и короткими объяснениями.

6. Формальность — формальное / неформальное / универсальное.

7. Американская транскрипция — в квадратных скобках, например: [ rɪˈzɪljənt ]

8. CEFR уровень (A1–C2), часть речи, формы слова:
   - если глагол: 3 формы + транскрипция
   - если прилагательное — степени сравнения
   - какие предлоги чаще всего следуют (с % частоты)

9. Коллокации — устойчивые словосочетания по уровням:
   - 🔹 A2–B1 (3–5 шт.)
   - 🔹 B2–C1 (3–5 шт.)

10. Идиомы — максимум 2–3 (если есть), если нет — написать, что нет.

11. Синонимы (3 шт.) + перевод и % заменяемости  
    Противоположное слово (антоним) — с переводом

12. Примеры (4 шт.):
   - короткие (до 12 слов)
   - с переводом
   - поясни, почему слово используется именно так

13. Мини-диалог из 4 реплик — на основе примеров выше, из повседневной городской жизни. Укажи контекст диалога (например: «в офисе», «на встрече», «по телефону»).

Объяснение пиши только на русском. Примеры на английском + перевод.
Избегай общих формулировок. Работай строго по шаблону.
"""

# Основная функция
async def handle_word_analysis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()
    user_id = update.effective_user.id

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📘 Разбираю слово *{word}* по Holla English...",
        parse_mode="Markdown"
    )

    try:
        response = await client.chat.completions.create(
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

        # Озвучка самого слова
        await synthesize_and_send(
            text=word,
            chat_id=update.effective_chat.id,
            context=context
        )

        # Запись в Google Sheets (не вложенный список!)
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        append_to_sheet("Word_Analysis", [str(user_id), word, now])

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ Ошибка при разборе слова. Попробуй другое или повтори позже."
        )
        print("Word analysis error:", e)

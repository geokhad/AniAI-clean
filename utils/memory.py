
import time

# ⏱️ Словарь для хранения истории сообщений: {user_id: [(question, answer), ...]}
session_memory = {}

# ⏳ Словарь для хранения времени последнего взаимодействия
last_interaction_time = {}

# ⏱️ Время жизни сеанса — 10 минут
SESSION_TTL_SECONDS = 600

# 📥 Получить историю памяти для пользователя
def get_memory(user_id: int):
    now = time.time()
    last_time = last_interaction_time.get(user_id)

    if last_time and now - last_time > SESSION_TTL_SECONDS:
        # Истекло время — очистка
        session_memory.pop(user_id, None)

    last_interaction_time[user_id] = now
    return session_memory.get(user_id, [])

# 📤 Обновить память — сохранить новую пару вопрос-ответ
def update_memory(user_id: int, question: str, answer: str):
    history = get_memory(user_id)

    # Добавляем новую пару
    history.append((question, answer))

    # Обрезаем до 5 последних
    if len(history) > 5:
        history = history[-5:]

    session_memory[user_id] = history

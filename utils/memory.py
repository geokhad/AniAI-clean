import time

# Словарь для хранения истории сообщений по user_id
session_memory = {}

# Настройки
MAX_HISTORY = 5
TIMEOUT_SECONDS = 600  # 10 минут

def get_session_messages(user_id: int):
    now = time.time()
    history = session_memory.get(user_id, [])
    # Фильтруем устаревшие записи
    history = [item for item in history if now - item["timestamp"] <= TIMEOUT_SECONDS]
    session_memory[user_id] = history
    return [{"role": item["role"], "content": item["content"]} for item in history[-MAX_HISTORY:]]

def add_session_message(user_id: int, role: str, content: str):
    session_memory.setdefault(user_id, [])
    session_memory[user_id].append({
        "role": role,
        "content": content,
        "timestamp": time.time()
    })


# utils/spaced_memory.py

user_memory = {}

def get_user_memory(user_id):
    return user_memory.get(user_id, [])

def add_to_memory(user_id, word):
    if user_id not in user_memory:
        user_memory[user_id] = []
    if word not in user_memory[user_id]:
        user_memory[user_id].append(word)

def update_word_memory(user_id, word):
    """Обновить или добавить слово в память пользователя"""
    if user_id not in user_memory:
        user_memory[user_id] = []
    if word in user_memory[user_id]:
        user_memory[user_id].remove(word)
    user_memory[user_id].append(word)

def reset_memory(user_id):
    user_memory[user_id] = []

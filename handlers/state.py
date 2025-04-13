# handlers/state.py

active_translators = set()
active_imagers = set()
active_analyzers = set()
active_ask = set()
active_tts = set()  # ✅ Добавлено: режим озвучки

def clear_user_state(user_id: int):
    active_translators.discard(user_id)
    active_imagers.discard(user_id)
    active_analyzers.discard(user_id)
    active_ask.discard(user_id)
    active_tts.discard(user_id)  # ✅ сбрасываем TTS

def is_user_active(user_id: int) -> bool:
    return any([
        user_id in active_translators,
        user_id in active_imagers,
        user_id in active_analyzers,
        user_id in active_ask,
        user_id in active_tts,  # ✅ проверяем TTS
    ])

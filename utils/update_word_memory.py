import json
import os
from datetime import date, timedelta

def update_word_memory(user_id, word_text):
    json_path = os.path.join(os.path.dirname(__file__), "spaced_words.json")

    with open(json_path, "r", encoding="utf-8") as f:
        words = json.load(f)

    today = date.today()

    for word in words:
        if word["word"].lower() == word_text.lower():
            word["interval_stage"] += 1
            days_to_next = 2 ** word["interval_stage"]
            next_review_date = today + timedelta(days=days_to_next)

            word["last_review"] = today.isoformat()
            word["next_review"] = next_review_date.isoformat()
            break

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=4)
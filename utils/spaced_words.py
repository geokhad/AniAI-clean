import json
import os

json_path = os.path.join(os.path.dirname(__file__), "spaced_words.json")

with open(json_path, "r", encoding="utf-8") as f:
    spaced_words = json.load(f)
# utils/spaced_audio.py

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def speak_text(text: str, filename: str):
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )
        with open(filename, "wb") as f:
            f.write(response.content)
    except Exception as e:
        print(f"❌ Error during speech synthesis: {e}")


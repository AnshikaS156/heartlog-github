from groq import Groq
from django.conf import settings
import json

client = Groq(api_key=settings.GROQ_API_KEY)


def detect_emotion(diary_text):
    prompt = f"""
You are an emotion detection system.

Analyze the diary text and classify it into exactly ONE emotion
from this list:

happy, sad, angry, calm, anxious, neutral

Respond ONLY in valid JSON format.

Format:
{{
  "emotion": "sad",
  "confidence": 0.82
}}

Diary text:
\"\"\"{diary_text}\"\"\"
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a strict JSON generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )

        response_text = completion.choices[0].message.content.strip()
        data = json.loads(response_text)

        return data["emotion"].lower(), float(data["confidence"])

    except Exception as e:
        print("Groq error:", e)
        return "neutral", 0.5

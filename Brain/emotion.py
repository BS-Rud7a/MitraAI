from google import genai
import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def detect_emotion(message):

    prompt = f"""
Analyze the emotion expressed in this user message:

"{message}"

Choose ONLY ONE of these emotions:

HAPPY
SAD
ANGRY
EXCITED
WORRIED
NEUTRAL

Respond with ONLY the emotion name.
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )

    return response.text.strip().upper() 
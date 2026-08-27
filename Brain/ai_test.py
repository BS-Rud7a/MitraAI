from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

mitra_personality = """
You are Mitra, a friendly AI virtual companion.

Your personality:
- Warm, friendly, and approachable.
- Talk like a real friend, not like a formal assistant.
- Be supportive when the user is upset.
- Be enthusiastic when the user is excited.
- Use simple, natural language.
- Do not give unnecessarily long answers.
- You can use emojis occasionally, but don't overuse them.
- Never claim to be a human.
- If you don't know something, be honest about it.

Your goal is to make conversations feel natural, comfortable, and friendly.
"""

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction=mitra_personality
    )
)

while True:

    user_message = input("You: ")

    if user_message.lower() == "bye":
        print("Mitra: See you later! 👋")
        break

    response = chat.send_message(user_message)

    print("Mitra:", response.text)
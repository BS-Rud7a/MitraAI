from dotenv import load_dotenv
from google import genai
from google.genai import types
from memory import load_memory, add_memory
import os


# Load environment variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# -------------------------------
# MITRA'S PERSONALITY
# -------------------------------

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


# -------------------------------
# DECIDE WHAT TO REMEMBER
# -------------------------------

def should_remember(message):

    decision_prompt = f"""
You are helping an AI virtual friend decide whether something should
be saved as long-term memory about the user.

User message:
"{message}"

Save the information only if it contains useful personal information
such as:

- Name
- Hobbies
- Likes or dislikes
- Favorite things
- Important preferences
- Long-term goals
- Important personal information

Do NOT save:

- General questions
- Temporary conversation
- Greetings
- Small talk
- General knowledge
- Random statements

Respond with ONLY:

YES

or

NO
"""

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=decision_prompt
    )

    return response.text.strip().upper() == "YES"


# -------------------------------
# LOAD EXISTING MEMORY
# -------------------------------

memory = load_memory()

memory_context = f"""
Here is some information you remember about the user:

{memory}

Use this information naturally when it is relevant.

Do not mention that you are reading a memory file.
Do not reveal private information unnecessarily.
"""


# -------------------------------
# CREATE MITRA'S CHAT
# -------------------------------

chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=types.GenerateContentConfig(
        system_instruction=mitra_personality + memory_context
    )
)


# -------------------------------
# MAIN CONVERSATION LOOP
# -------------------------------

while True:

    user_message = input("You: ")

    # Exit the program
    if user_message.lower() == "bye":
        print("Mitra: See you later! 👋")
        break

    # Send message to Gemini
    response = chat.send_message(user_message)

    # Display Mitra's response
    print("Mitra:", response.text)

    # Check whether the message should be remembered
    print("DEBUG: Checking if this should be remembered...")

    decision = should_remember(user_message)

    print("DEBUG: Memory decision =", decision)

    # Save the message if Gemini decides it is important
    if decision:
        add_memory(user_message)
        print("💾 Mitra remembered that.")
    else:
        print("❌ Mitra decided not to remember.")
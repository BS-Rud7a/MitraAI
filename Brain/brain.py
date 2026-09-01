from dotenv import load_dotenv
from google import genai
from google.genai import types

from Brain.memory import load_memory, add_memory
from NLP.nlp_module import detect_language, translate, detect_emotion
from Voice.tts import speak

import os


# -------------------------------
# LOAD ENVIRONMENT
# -------------------------------

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
# MAIN MITRA FUNCTION
# -------------------------------

def mitra_response(user_message):
    """
    Process a user's message and return Mitra's response.

    The GUI will call this function.
    """

    # Detect language
    language = detect_language(user_message)

    # Detect emotion
    emotion = detect_emotion(user_message)

    emotion_label = emotion["label"]

    # Translate user's message to English
    english_message = translate(
        user_message,
        target_lang="en",
        source_lang=language
    )

    # Generate Mitra's response
    response = chat.send_message(
        f"""
The user's emotional state is: {emotion_label}.

The user originally wrote in language: {language}.

Use the emotional information only to adjust your tone.
Do not mention the emotion detection.
Do not mention translation.

Reply naturally as Mitra.
Keep the response friendly and conversational.
Do not explain your reasoning.

User message:
{english_message}
"""
    )

    mitra_text = response.text

    # Translate response back to user's language
    if language != "en":
        mitra_text = translate(
            mitra_text,
            target_lang=language,
            source_lang="en"
        )

    # Speak the response
    speak(mitra_text, language)

    # Check memory
    decision = should_remember(user_message)

    if decision:
        add_memory(user_message)

    # Return response to the GUI
    return mitra_text


# -------------------------------
# TERMINAL TEST MODE
# -------------------------------

if __name__ == "__main__":

    while True:

        user_message = input("You: ")

        if user_message.lower() == "bye":
            print("Mitra: See you later! 👋")
            break

        response = mitra_response(user_message)

        print("Mitra:", response)
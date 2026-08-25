def mitra_response(message):

    message = message.lower()

    if "hello" in message or "hi" in message:
        return "Hey! It's good to hear from you! 😊"

    elif "how are you" in message:
        return "I'm doing great! Thanks for asking! How are you?"

    elif "bye" in message:
        return "See you later! 👋"
    elif "what is your name" in message:
        return "I am Mitra, your mitra  "
    else:
        return "Hmm, tell me more about that."


user_message = input("You: ")

response = mitra_response(user_message)

print("Mitra:", response) 
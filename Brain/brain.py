def mitra_response(message):
    return "Hey! I heard you say: " + message


user_message = input("You: ")

response = mitra_response(user_message)

print("Mitra:", response)
from tts import speak

# Simulated AI response
response = "I understand how you feel. I am here to talk with you."

# Simulated detected language
language = "en"

# Send AI response to TTS
audio_file = speak(response, language)

print("Mitra response generated:", audio_file)
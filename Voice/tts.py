import os
import time
from supertonic import TTS

tts = TTS(auto_download=True)

voice = tts.get_voice_style(voice_name="F1")


def speak(text, language):
    supported_languages = ["en", "hi", "es", "fr"]

    if language not in supported_languages:
        raise ValueError(
            f"Unsupported language: {language}. "
            f"Use one of: {supported_languages}"
        )

    if not text or not text.strip():
        raise ValueError("Text cannot be empty")

    wav, duration = tts.synthesize(
        text=text,
        voice_style=voice,
        lang=language
    )

    filename = f"mitra_response_{int(time.time())}.wav"

    tts.save_audio(wav, filename)

    os.startfile(filename)

    return filename
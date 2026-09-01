import os
import tempfile

import sounddevice as sd
import soundfile as sf
from supertonic import TTS


# Load the TTS model once
tts = TTS(auto_download=True)

# Load Mitra's voice style
voice = tts.get_voice_style(voice_name="F1")


def speak(text, language):
    """
    Generate and play Mitra's response.

    The audio file is temporary and is deleted
    automatically after playback.
    """

    supported_languages = ["en", "hi", "es", "fr"]

    if language not in supported_languages:
        language = "en"
    # Generate the speech
    wav, duration = tts.synthesize(
        text=text,
        voice_style=voice,
        lang=language
    )

    temp_file = None

    try:
        # Create a temporary WAV file
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as file:
            temp_file = file.name

        # Save the generated audio temporarily
        tts.save_audio(wav, temp_file)

        # Read the temporary audio
        audio, sample_rate = sf.read(temp_file)

        # Play it and wait until playback finishes
        sd.play(audio, sample_rate)
        sd.wait()

    finally:
        # Delete the temporary WAV file
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
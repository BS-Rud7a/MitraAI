import os
import tempfile

import sounddevice as sd
import soundfile as sf
from supertonic import TTS


# =========================================================
# LOAD TTS MODEL
# =========================================================

tts = TTS(auto_download=True)


# =========================================================
# LOAD MITRA'S VOICE
# =========================================================

voice = tts.get_voice_style(
    voice_name="F1"
)


# =========================================================
# SPEECH CALLBACKS
# =========================================================

speech_started_callback = None
speech_finished_callback = None


def set_speech_callbacks(
    on_start=None,
    on_finish=None
):
    """
    Set functions that are called when
    Mitra starts and finishes speaking.
    """

    global speech_started_callback
    global speech_finished_callback

    speech_started_callback = on_start
    speech_finished_callback = on_finish


# =========================================================
# SPEAK
# =========================================================

def speak(text, language):
    """
    Generate and play Mitra's response.

    The audio file is temporary and is deleted
    automatically after playback.
    """

    supported_languages = [
        "en",
        "hi",
        "es",
        "fr"
    ]

    # Fallback for unsupported languages
    if language not in supported_languages:
        language = "en"

    # -----------------------------------------------------
    # Generate speech
    # -----------------------------------------------------

    wav, duration = tts.synthesize(
        text=text,
        voice_style=voice,
        lang=language
    )

    temp_file = None

    try:

        # -------------------------------------------------
        # Create temporary WAV file
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False
        ) as file:

            temp_file = file.name

        # -------------------------------------------------
        # Save generated audio
        # -------------------------------------------------

        tts.save_audio(
            wav,
            temp_file
        )

        # -------------------------------------------------
        # Read audio
        # -------------------------------------------------

        audio, sample_rate = sf.read(
            temp_file
        )

        # -------------------------------------------------
        # Tell GUI that speaking started
        # -------------------------------------------------

        if speech_started_callback:

            speech_started_callback()

        # -------------------------------------------------
        # Play audio
        # -------------------------------------------------

        sd.play(
            audio,
            sample_rate
        )

        sd.wait()

        # -------------------------------------------------
        # Tell GUI that speaking finished
        # -------------------------------------------------

        if speech_finished_callback:

            speech_finished_callback()

    finally:

        # -------------------------------------------------
        # Delete temporary audio file
        # -------------------------------------------------

        if temp_file and os.path.exists(
            temp_file
        ):

            os.remove(
                temp_file
            )
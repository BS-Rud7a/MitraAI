import sounddevice as sd
import scipy.io.wavfile as wav
import whisper
import numpy as np
import time

from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate


# ==================================================
# SETTINGS
# ==================================================

SAMPLE_RATE = 16000
MODEL_NAME = "small"

BLOCK_DURATION = 0.1

# How long user must be silent before recording stops
SILENCE_DURATION = 2.0

# Prevent infinite recording
MAX_RECORDING_DURATION = 30

# Wait for user to start speaking
START_TIMEOUT = 15

# Microphone sensitivity
SILENCE_THRESHOLD = 300


# ==================================================
# LOAD WHISPER MODEL
# ==================================================

print("Loading Whisper model...")

model = whisper.load_model(MODEL_NAME)

print("Model loaded successfully!")


# ==================================================
# HINGLISH DETECTION
# ==================================================

# Common Roman-Hindi words. This is only used as a
# safety net when Whisper incorrectly labels Hinglish
# as English.
HINGLISH_WORDS = {
    "aap", "aapko", "aapki",
    "aaj", "abhi", "acha", "accha",
    "aur", "batao", "baat",
    "bhai", "bhi", "chal", "chalo",
    "hai", "hain", "ho", "hua",
    "kaise", "kaisa", "kaisi",
    "kar", "karo", "karna", "karne",
    "kya", "kyun", "kyon",
    "main", "mein", "mujhe",
    "mera", "meri", "mere",
    "mita", "mitra",
    "nahi", "nahin",
    "tum", "tumhe", "tumhara", "tumhari",
    "tha", "thi", "the",
    "to", "toh",
    "yaar", "ya",
}


def looks_like_hinglish(text):
    """
    Detect likely Roman Hindi/Hinglish in text.

    This is deliberately conservative so normal English
    sentences are not repeatedly transcribed as Hindi.
    """

    words = {
        word.strip(".,!?;:'\"()[]{}").lower()
        for word in text.split()
    }

    matches = words.intersection(HINGLISH_WORDS)

    return len(matches) >= 2


# ==================================================
# SELECT LANGUAGE
# ==================================================

def select_language():

    while True:

        print("\nSelect speaking language:")
        print("1. English")
        print("2. Hindi")

        choice = input("\nEnter 1 or 2: ").strip()

        if choice == "1":
            return "en", "English"

        elif choice == "2":
            return "hi", "Hindi"

        else:
            print("Invalid choice. Please try again.")


# ==================================================
# RECORD UNTIL USER STOPS SPEAKING
# ==================================================

def record_until_silence():

    block_size = int(
        SAMPLE_RATE * BLOCK_DURATION
    )

    audio_chunks = []

    speaking_started = False
    silence_time = 0
    start_time = time.time()
    speech_start_time = None

    print("\n🎤 Listening...")
    print("Start speaking when ready.")

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        blocksize=block_size
    ) as stream:

        while True:

            audio_block, overflowed = stream.read(
                block_size
            )

            volume = np.sqrt(
                np.mean(
                    audio_block.astype(np.float32) ** 2
                )
            )

            current_time = time.time()

            # ==========================================
            # WAITING FOR SPEECH
            # ==========================================

            if not speaking_started:

                if volume > SILENCE_THRESHOLD:

                    speaking_started = True
                    speech_start_time = current_time

                    print("🟢 Speech detected. Keep talking...")

                    audio_chunks.append(
                        audio_block.copy()
                    )

                elif (
                    current_time - start_time
                    > START_TIMEOUT
                ):

                    print("⚠️ No speech detected.")
                    return None

            # ==========================================
            # SPEECH HAS STARTED
            # ==========================================

            else:

                audio_chunks.append(
                    audio_block.copy()
                )

                if volume < SILENCE_THRESHOLD:

                    silence_time += BLOCK_DURATION

                else:

                    silence_time = 0

                if silence_time >= SILENCE_DURATION:

                    print("🔴 You stopped speaking.")
                    break

                if (
                    current_time - speech_start_time
                    >= MAX_RECORDING_DURATION
                ):

                    print("⚠️ Maximum recording time reached.")
                    break

    if len(audio_chunks) == 0:

        return None

    audio = np.concatenate(
        audio_chunks,
        axis=0
    )

    return audio


# ==================================================
# CONVERT HINDI TO ROMAN HINDI
# ==================================================

def hindi_to_roman(text):

    try:

        # If Whisper already returned Roman text,
        # don't transliterate it again.
        devanagari_count = sum(
            "\u0900" <= character <= "\u097F"
            for character in text
        )

        if devanagari_count == 0:

            return text

        roman_text = transliterate(
            text,
            sanscript.DEVANAGARI,
            sanscript.ITRANS
        )

        # Make common ITRANS nasal notation easier to read.
        roman_text = roman_text.replace("M", "n")
        roman_text = roman_text.replace("N", "n")

        return roman_text

    except Exception:

        return text


# ==================================================
# TRANSCRIBE
# ==================================================

def transcribe_audio(language_code):

    options = {
        "task": "transcribe",
        "fp16": False,

        # Stronger decoding than the previous beam_size=1.
        "beam_size": 5,
        "best_of": 5,

        "temperature": 0,
        "condition_on_previous_text": False,

        # Reduce empty/hallucinated results.
        "no_speech_threshold": 0.6,
        "logprob_threshold": -1.0,
        "compression_ratio_threshold": 2.4,
    }

    if language_code in ("en", "hi"):

        options["language"] = language_code

    else:

        options["language"] = None

    return model.transcribe(
        "recording.wav",
        **options
    )


# ==================================================
# MAIN SPEECH TO TEXT
# ==================================================

def speech_to_text(language_code=None):

    recording_start = time.time()

    audio = record_until_silence()

    if audio is None:

        print("No audio recorded.")
        return None

    recording_time = (
        time.time() - recording_start
    )

    wav.write(
        "recording.wav",
        SAMPLE_RATE,
        audio
    )

    print("✅ Recording saved.")

    print("\n🧠 Converting speech to text...")

    transcription_start = time.time()

    # First pass.
    result = transcribe_audio(language_code)

    text = result.get(
        "text",
        ""
    ).strip()

    detected_language = result.get(
        "language",
        language_code or "en"
    )

    # ==================================================
    # HINDI / HINGLISH SAFETY NET
    # ==================================================
    #
    # Whisper can mistake Hindi/Hinglish for English or
    # occasionally another language.
    #
    # If auto-detection gives another language, retry
    # as Hindi.
    #
    # If it gives English but the transcription contains
    # several common Roman-Hindi words, retry as Hindi too.
    #

    should_retry_hindi = False

    if language_code is None:

        if detected_language not in ("en", "hi"):

            should_retry_hindi = True

        elif (
            detected_language == "en"
            and looks_like_hinglish(text)
        ):

            should_retry_hindi = True

    if should_retry_hindi:

        print(
            f"⚠️ Whisper detected '{detected_language}'. "
            "Trying Hindi..."
        )

        hindi_result = transcribe_audio("hi")

        hindi_text = hindi_result.get(
            "text",
            ""
        ).strip()

        if hindi_text:

            result = hindi_result
            text = hindi_text
            detected_language = "hi"

    # Keep only languages Mitra currently supports.
    if detected_language not in ("en", "hi"):

        detected_language = "en"

    transcription_time = (
        time.time() - transcription_start
    )

    # ==================================================
    # ROMANIZE HINDI
    # ==================================================

    if detected_language == "hi":

        output_text = hindi_to_roman(text)

    else:

        output_text = text

    # ==================================================
    # RESULTS
    # ==================================================

    print("\n" + "=" * 60)

    print("🎤 MITRA AI - SPEECH TO TEXT")

    print("=" * 60)

    print(
        f"\n🌍 Language: {detected_language}"
    )

    print(
        "\n📝 Recognized Text:"
    )

    print(
        output_text
    )

    print(
        "\n⏱️ PERFORMANCE"
    )

    print(
        f"Recording time: "
        f"{recording_time:.2f} seconds"
    )

    print(
        f"Transcription time: "
        f"{transcription_time:.2f} seconds"
    )

    print(
        f"Total time: "
        f"{recording_time + transcription_time:.2f} seconds"
    )

    print("=" * 60)

    # Return the actual language used/detected.
    return {
        "text": output_text,
        "language": detected_language
    }


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    speech_to_text()

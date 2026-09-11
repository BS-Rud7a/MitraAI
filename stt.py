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
MODEL_NAME = "base"

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


            # Calculate microphone volume

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

                    print(
                        "⚠️ No speech detected."
                    )

                    return None


            # ==========================================
            # SPEECH HAS STARTED
            # ==========================================

            else:


                audio_chunks.append(
                    audio_block.copy()
                )


                # Check for silence

                if volume < SILENCE_THRESHOLD:

                    silence_time += BLOCK_DURATION

                else:

                    # User started speaking again

                    silence_time = 0


                # ======================================
                # STOP AFTER 2 SECONDS SILENCE
                # ======================================

                if silence_time >= SILENCE_DURATION:

                    print(
                        "🔴 You stopped speaking."
                    )

                    break


                # ======================================
                # SAFETY LIMIT
                # ======================================

                if (

                    current_time

                    - speech_start_time

                    >= MAX_RECORDING_DURATION

                ):

                    print(
                        "⚠️ Maximum recording time reached."
                    )

                    break


    # ==============================================
    # COMBINE AUDIO
    # ==============================================

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

        roman_text = transliterate(

            text,

            sanscript.DEVANAGARI,

            sanscript.ITRANS

        )


        return roman_text


    except Exception:

        return text


# ==================================================
# MAIN SPEECH TO TEXT
# ==================================================

def speech_to_text(language_code=None):


    # ==============================================
    # LANGUAGE
    # ==============================================

    # None means Whisper automatically detects
    # whether the user is speaking English or Hindi.


    # ==============================================
    # RECORD
    # ==============================================

    recording_start = time.time()


    audio = record_until_silence()


    if audio is None:

        print("No audio recorded.")

        return None


    recording_time = (

        time.time()

        - recording_start

    )


    # ==============================================
    # SAVE AUDIO
    # ==============================================

    wav.write(

        "recording.wav",

        SAMPLE_RATE,

        audio

    )


    print("✅ Recording saved.")


    # ==============================================
    # TRANSCRIBE
    # ==============================================

    print("\n🧠 Converting speech to text...")


    transcription_start = time.time()


    result = model.transcribe(

        "recording.wav",

        language=language_code,

        task="transcribe",

        fp16=False,

        temperature=0,

        beam_size=1,

        best_of=1,

        condition_on_previous_text=False

    )


    transcription_time = (

        time.time()

        - transcription_start

    )


    text = result["text"].strip()

    detected_language = result.get("language", "en")

    if detected_language not in ["en", "hi"]:
        detected_language = "en"


    # ==============================================
    # ROMANIZE HINDI
    # ==============================================

    if detected_language == "hi":

        output_text = hindi_to_roman(text)

    else:

        output_text = text


    # ==============================================
    # RESULTS
    # ==============================================

    print("\n" + "=" * 60)

    print("🎤 MITRA AI - SPEECH TO TEXT")

    print("=" * 60)


    print(

        f"\n🌍 Language: "

        f"{detected_language}"

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


    # ==============================================
    # RETURN FOR INTEGRATION
    # ==============================================

    return {

        "text": output_text,

        "language": language_code

    }


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    speech_to_text()
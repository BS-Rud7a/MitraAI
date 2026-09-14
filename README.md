# Mitra AI

An emotion-aware multilingual AI virtual companion built using Python, Machine Learning, NLP, speech processing, and text-to-speech technologies.

## Project Overview

Mitra AI is a voice-enabled virtual companion designed to communicate naturally with users through text and speech.

The system combines an AI language model with Natural Language Processing, emotion detection, multilingual translation, speech recognition, memory, and text-to-speech to create a more interactive conversational experience.

## Problem Statement

Traditional chatbots often provide text-based responses without considering the user's language, emotional state, or conversational context.

Mitra AI aims to create a more natural and engaging AI companion by combining multilingual communication, emotion awareness, voice interaction, and memory within a single application.

## Objectives

- Develop an interactive AI virtual companion.
- Support multilingual conversations.
- Detect the emotional tone of user messages.
- Enable speech-to-text voice interaction.
- Convert Mitra's responses into speech.
- Remember important information provided by the user.
- Provide an intuitive graphical user interface.

## Key Features

- AI-powered conversational responses
- Multilingual language detection
- English and Hindi/Hinglish support
- Machine translation
- Emotion detection
- Speech-to-text using Whisper
- Text-to-speech using Supertonic
- Persistent user memory
- Animated virtual avatar
- Graphical user interface
- Voice input through microphone
- Settings and memory viewer

## Technologies Used

- Python
- Machine Learning
- Natural Language Processing (NLP)
- Google Gemini API
- Whisper
- NLLB Machine Translation
- Emotion Classification
- Supertonic Text-to-Speech
- PySide6
- SoundDevice
- JSON-based Memory Storage

## System Architecture

```text
                    ┌─────────────────┐
                    │     User        │
                    └────────┬────────┘
                             │
                    Text / Voice Input
                             │
                             ▼
                    ┌─────────────────┐
                    │  Speech-to-Text │
                    │     Whisper     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   NLP Module    │
                    │                 │
                    │ Language Detect │
                    │ Translation     │
                    │ Emotion Detect  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Mitra Brain   │
                    │  Gemini API     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Memory System   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Response NLP   │
                    │  & Translation  │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │   Text Response │       │ Text-to-Speech  │
       │      GUI        │       │   Supertonic    │
       └─────────────────┘       └────────┬────────┘
                                          │
                                          ▼
                                  ┌─────────────────┐
                                  │ Animated Avatar │
                                  └─────────────────┘

Yep — this is **way too bare for a final submission**. But that's actually good because we can improve it quickly without touching the code.

I’d replace your README with this:

````markdown
# Mitra AI

An emotion-aware multilingual AI virtual companion built using Python, Machine Learning, NLP, speech processing, and text-to-speech technologies.

## Project Overview

Mitra AI is a voice-enabled virtual companion designed to communicate naturally with users through text and speech.

The system combines an AI language model with Natural Language Processing, emotion detection, multilingual translation, speech recognition, memory, and text-to-speech to create a more interactive conversational experience.

## Problem Statement

Traditional chatbots often provide text-based responses without considering the user's language, emotional state, or conversational context.

Mitra AI aims to create a more natural and engaging AI companion by combining multilingual communication, emotion awareness, voice interaction, and memory within a single application.

## Objectives

- Develop an interactive AI virtual companion.
- Support multilingual conversations.
- Detect the emotional tone of user messages.
- Enable speech-to-text voice interaction.
- Convert Mitra's responses into speech.
- Remember important information provided by the user.
- Provide an intuitive graphical user interface.

## Key Features

- AI-powered conversational responses
- Multilingual language detection
- English and Hindi/Hinglish support
- Machine translation
- Emotion detection
- Speech-to-text using Whisper
- Text-to-speech using Supertonic
- Persistent user memory
- Animated virtual avatar
- Graphical user interface
- Voice input through microphone
- Settings and memory viewer

## Technologies Used

- Python
- Machine Learning
- Natural Language Processing (NLP)
- Google Gemini API
- Whisper
- NLLB Machine Translation
- Emotion Classification
- Supertonic Text-to-Speech
- PySide6
- SoundDevice
- JSON-based Memory Storage

## System Architecture

```text
                    ┌─────────────────┐
                    │     User        │
                    └────────┬────────┘
                             │
                    Text / Voice Input
                             │
                             ▼
                    ┌─────────────────┐
                    │  Speech-to-Text │
                    │     Whisper     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   NLP Module    │
                    │                 │
                    │ Language Detect │
                    │ Translation     │
                    │ Emotion Detect  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Mitra Brain   │
                    │  Gemini API     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Memory System   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  Response NLP   │
                    │  & Translation  │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
       ┌─────────────────┐       ┌─────────────────┐
       │   Text Response │       │ Text-to-Speech  │
       │      GUI        │       │   Supertonic    │
       └─────────────────┘       └────────┬────────┘
                                          │
                                          ▼
                                  ┌─────────────────┐
                                  │ Animated Avatar │
                                  └─────────────────┘
```

## Machine Learning & NLP Components

### Language Detection

Mitra identifies the language of the user's message and processes it accordingly.

### Machine Translation

The NLP module uses the NLLB machine translation model to translate supported languages when required.

### Emotion Detection

Mitra analyzes English text to identify the emotional tone of the user's message and uses this information as part of the conversational response process.

### Speech Recognition

Voice input is processed using Whisper Small to convert spoken language into text.

### Text-to-Speech

Mitra uses Supertonic to generate spoken responses using a selected voice.

## Memory

Mitra includes a persistent memory system that stores important facts provided by the user.

Memory is stored locally in JSON format and can be viewed through the application's memory viewer.

## Graphical User Interface

The application is built using PySide6 and includes:

* Chat interface
* Animated Mitra avatar
* Microphone input
* Send button
* Settings panel
* Language selection
* Memory viewer
* Conversation status indicators

## Project Structure

```text
MitraAI/
│
├── Brain/
│   ├── brain.py
│   ├── memory.py
│   └── memory.json
│
├── NLP/
│   └── nlp_module.py
│
├── Voice/
│   └── tts.py
│
├── UI/
│   ├── main.py
│   └── assets/
│
├── stt.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd MitraAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_api_key_here
```

Do not commit the `.env` file or expose the API key publicly.

### 6. Run Mitra

```bash
python UI/main.py
```

## Limitations

* Speech recognition accuracy can vary depending on environmental noise.
* Hindi/Hinglish speech recognition may be less accurate than English in some conditions.
* Emotion detection is primarily applied to English text.
* Internet connectivity is required for the Gemini-powered conversational component.
* Voice generation and machine translation require additional computational resources.

## Future Scope

Future versions of Mitra could include:

* Improved multilingual speech recognition
* More advanced long-term memory
* Personalized conversations
* More sophisticated emotion understanding
* Additional voice and language options
* Offline AI capabilities
* Alternative AI model providers
* More advanced avatar interaction

## Conclusion

Mitra AI demonstrates how Machine Learning, Natural Language Processing, speech recognition, machine translation, emotion detection, and text-to-speech can be combined to create an interactive AI companion.

The project focuses on making human-AI interaction more natural through multilingual communication, emotional awareness, voice interaction, memory, and an interactive graphical interface.


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
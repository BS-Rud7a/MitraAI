"""
Mitra AI - NLP / Translation module

Exposes three functions for the rest of the team to call:
    detect_language(text)          -> "en" | "hi" | "es" | "fr" | ...
    translate(text, target_lang)   -> translated text (auto-detects source language)
    detect_emotion(text)           -> {"label": "sadness", "score": 0.91}

Everything runs locally after the first download (models are cached in
~/.cache/huggingface). No API keys, no internet required after setup.
"""

from langdetect import detect as _langdetect, DetectorFactory
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# langdetect samples internally at random by default, which means it can give
# a different (sometimes wrong) answer on different runs of the same text.
# Seeding it makes results deterministic and repeatable.
DetectorFactory.seed = 0

# ---------------------------------------------------------------------------
# Language codes: NLLB uses "FLORES-200" codes, not plain ISO codes.
# Add more here if the team wants to support more languages later.
# ---------------------------------------------------------------------------
_NLLB_LANG_CODE = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "es": "spa_Latn",
    "fr": "fra_Latn",
}

_translation_tokenizer = None
_translation_model = None
_emotion_classifier = None

# Common Romanized Hindi ("Hinglish") words. langdetect only understands
# native scripts, so Hindi typed in English letters (e.g. "mujhe bura lag
# raha hai") gets misread as random other languages. If a chunk of these
# common words show up, we trust that over langdetect's guess.
_HINGLISH_WORDS = {
    "hai", "hain", "mujhe", "mera", "meri", "tumhe", "tum", "aap", "kya",
    "kyu", "kyun", "kaise", "kaisa", "bahut", "bura", "accha", "acha",
    "raha", "rahi", "rahe", "nahi", "nahin", "haan", "kar", "karo",
    "karna", "lag", "aaj", "kal", "abhi", "bhi", "toh", "hoon", "hum",
}


def _looks_like_hinglish(text: str) -> bool:
    words = text.lower().replace(".", "").replace(",", "").split()
    if not words:
        return False
    hits = sum(1 for w in words if w in _HINGLISH_WORDS)
    return hits >= 2 or (hits >= 1 and len(words) <= 4)


# Common English function words. langdetect is unreliable on short
# sentences and can misread plain English as an unrelated language
# (e.g. "I failed my exam today." as Somali). If enough of these common
# words show up, we trust that over langdetect's guess.
_ENGLISH_WORDS = {
    "the", "is", "a", "an", "i", "my", "you", "your", "he", "she", "it",
    "we", "they", "today", "yesterday", "tomorrow", "am", "are", "was",
    "were", "have", "has", "had", "do", "does", "did", "not", "and",
    "or", "but", "to", "of", "in", "on", "at", "for", "with", "this",
    "that", "me", "him", "her",
}


def _looks_like_english(text: str) -> bool:
    words = text.lower().replace(".", "").replace(",", "").split()
    if not words:
        return False
    hits = sum(1 for w in words if w in _ENGLISH_WORDS)
    return hits >= 2


def _get_translation_model():
    """
    Lazily load the NLLB tokenizer + model directly (loads once, reused after).
    We load the model/tokenizer directly rather than via pipeline("translation", ...)
    because newer transformers versions removed that pipeline shortcut.
    """
    global _translation_tokenizer, _translation_model
    if _translation_model is None:
        _translation_tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-distilled-600M")
        _translation_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    return _translation_tokenizer, _translation_model


def _get_emotion_classifier():
    """Lazily load the English emotion classifier (loads once, reused after)."""
    global _emotion_classifier
    if _emotion_classifier is None:
        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=1,
        )
    return _emotion_classifier


def detect_language(text: str) -> str:
    """
    Returns a short ISO code like 'en', 'hi', 'es', 'fr'.
    Falls back to 'en' if detection fails on very short input.
    Overrides langdetect's guess if the text looks like Romanized Hindi,
    since langdetect only recognizes native scripts.
    """
    if _looks_like_hinglish(text):
        return "hi"
    if _looks_like_english(text):
        return "en"
    try:
        return _langdetect(text)
    except Exception:
        return "en"


def translate(text: str, target_lang: str, source_lang: str = None) -> str:
    """
    Translates `text` into `target_lang` (e.g. 'en', 'hi', 'es', 'fr').
    If `source_lang` is not given, it is auto-detected.
    """
    if source_lang is None:
        source_lang = detect_language(text)

    if source_lang == target_lang:
        return text  # nothing to do

    src_code = _NLLB_LANG_CODE.get(source_lang, "eng_Latn")
    tgt_code = _NLLB_LANG_CODE.get(target_lang, "eng_Latn")

    tokenizer, model = _get_translation_model()
    tokenizer.src_lang = src_code

    inputs = tokenizer(text, return_tensors="pt")

    # Newer tokenizer versions expose language codes as regular tokens;
    # older ones expose a lang_code_to_id dict. Handle both.
    if hasattr(tokenizer, "lang_code_to_id"):
        forced_bos_token_id = tokenizer.lang_code_to_id[tgt_code]
    else:
        forced_bos_token_id = tokenizer.convert_tokens_to_ids(tgt_code)

    generated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=forced_bos_token_id,
        max_length=200,
    )
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]


def detect_emotion(text: str) -> dict:
    """
    Returns the dominant emotion, e.g. {"label": "sadness", "score": 0.91}.
    Non-English text is translated to English first, since the emotion
    model itself is English-only.
    """
    lang = detect_language(text)
    english_text = translate(text, target_lang="en", source_lang=lang) if lang != "en" else text

    classifier = _get_emotion_classifier()
    result = classifier(english_text)[0][0]  # top_k=1 -> list of one dict
    return {"label": result["label"], "score": round(result["score"], 3)}


# ---------------------------------------------------------------------------
# Quick manual test - run `python nlp_module.py` to sanity-check the module
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    samples = [
        "I failed my exam today.",
        "Mujhe aaj bahut bura lag raha hai.",
        "Estoy muy feliz hoy.",
    ]
    for s in samples:
        lang = detect_language(s)
        en = translate(s, target_lang="en", source_lang=lang)
        emotion = detect_emotion(s)
        print(f"Text: {s}")
        print(f"  Detected language: {lang}")
        print(f"  English: {en}")
        print(f"  Emotion: {emotion}")
        print()

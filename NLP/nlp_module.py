"""
Mitra AI - NLP / Translation module

Provides:

    detect_language(text)
        -> "en" | "hi" | "es" | "fr" | ...

    translate(text, target_lang, source_lang=None)
        -> translated text

    detect_emotion(text)
        -> {"label": "sadness", "score": 0.91}

The translation and emotion models run locally after their
initial download and are cached by Hugging Face.
"""

from langdetect import detect as _langdetect, DetectorFactory
from transformers import (
    pipeline,
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


# =========================================================
# LANGUAGE DETECTION
# =========================================================

DetectorFactory.seed = 0


# =========================================================
# NLLB LANGUAGE CODES
# =========================================================

_NLLB_LANG_CODE = {

    "en": "eng_Latn",

    "hi": "hin_Deva",

    "es": "spa_Latn",

    "fr": "fra_Latn",
}


# =========================================================
# MODEL VARIABLES
# =========================================================

_translation_tokenizer = None
_translation_model = None

_emotion_classifier = None


# =========================================================
# HINGLISH DETECTION
# =========================================================

_HINGLISH_WORDS = {

    "hai",
    "hain",
    "mujhe",
    "mera",
    "meri",
    "mere",
    "tumhe",
    "tum",
    "tumhara",
    "tumhari",
    "aap",
    "kya",
    "kyu",
    "kyun",
    "kaise",
    "kaisa",
    "kaisi",
    "bahut",
    "bura",
    "accha",
    "acha",
    "raha",
    "rahi",
    "rahe",
    "nahi",
    "nahin",
    "haan",
    "kar",
    "karo",
    "karna",
    "karu",
    "lag",
    "aaj",
    "kal",
    "abhi",
    "bhi",
    "toh",
    "to",
    "hoon",
    "hum",
    "yaar",
    "kyunki",
    "lekin",
    "mujhse",
    "tera",
    "teri",
    "tere",
    "apna",
    "apni",
    "apne",
    "chahiye",
    "sakta",
    "sakti",
    "sakte",
}


def _looks_like_hinglish(text: str) -> bool:

    words = (
        text
        .lower()
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .split()
    )

    if not words:

        return False

    hits = sum(
        1
        for word in words
        if word in _HINGLISH_WORDS
    )

    return (
        hits >= 2
        or (hits >= 1 and len(words) <= 4)
    )


# =========================================================
# ENGLISH DETECTION
# =========================================================

_ENGLISH_WORDS = {

    "the",
    "is",
    "a",
    "an",
    "i",
    "my",
    "you",
    "your",
    "he",
    "she",
    "it",
    "we",
    "they",
    "today",
    "yesterday",
    "tomorrow",
    "am",
    "are",
    "was",
    "were",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "not",
    "and",
    "or",
    "but",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "with",
    "this",
    "that",
    "me",
    "him",
    "her",
}


def _looks_like_english(text: str) -> bool:

    words = (
        text
        .lower()
        .replace(".", "")
        .replace(",", "")
        .replace("!", "")
        .replace("?", "")
        .split()
    )

    if not words:

        return False

    hits = sum(
        1
        for word in words
        if word in _ENGLISH_WORDS
    )

    return hits >= 2


# =========================================================
# LOAD TRANSLATION MODEL
# =========================================================

def _get_translation_model():

    global _translation_tokenizer
    global _translation_model

    if _translation_model is None:

        _translation_tokenizer = (
            AutoTokenizer.from_pretrained(
                "facebook/nllb-200-distilled-600M"
            )
        )

        _translation_model = (
            AutoModelForSeq2SeqLM.from_pretrained(
                "facebook/nllb-200-distilled-600M"
            )
        )

    return (
        _translation_tokenizer,
        _translation_model
    )


# =========================================================
# LOAD EMOTION MODEL
# =========================================================

def _get_emotion_classifier():

    global _emotion_classifier

    if _emotion_classifier is None:

        _emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            top_k=1,
        )

    return _emotion_classifier


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text: str) -> str:
    """
    Detect the user's language.

    Supports:
        English
        Hindi
        Hinglish
        Spanish
        French

    Romanized Hindi is detected separately because
    langdetect does not reliably recognize Hinglish.
    """

    if _looks_like_hinglish(text):

        return "hi"

    if _looks_like_english(text):

        return "en"

    try:

        return _langdetect(text)

    except Exception:

        return "en"


# =========================================================
# BASIC NLLB TRANSLATION
# =========================================================

def _nllb_translate(
    text: str,
    target_lang: str,
    source_lang: str
) -> str:

    if source_lang == target_lang:

        return text

    src_code = _NLLB_LANG_CODE.get(
        source_lang,
        "eng_Latn"
    )

    tgt_code = _NLLB_LANG_CODE.get(
        target_lang,
        "eng_Latn"
    )

    tokenizer, model = _get_translation_model()

    tokenizer.src_lang = src_code

    inputs = tokenizer(
        text,
        return_tensors="pt"
    )

    # -----------------------------------------------------
    # Determine target language token
    # -----------------------------------------------------

    if hasattr(
        tokenizer,
        "lang_code_to_id"
    ):

        forced_bos_token_id = (
            tokenizer
            .lang_code_to_id[tgt_code]
        )

    else:

        forced_bos_token_id = (
            tokenizer.convert_tokens_to_ids(
                tgt_code
            )
        )

    # -----------------------------------------------------
    # Generate translation
    # -----------------------------------------------------

    generated_tokens = model.generate(
        **inputs,
        forced_bos_token_id=forced_bos_token_id,
        max_length=200,
    )

    translated_text = (
        tokenizer
        .batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]
    )

    return translated_text


# =========================================================
# CASUAL HINDI CONVERSION
# =========================================================

def _make_hindi_conversational(
    translated_text: str
) -> str:
    """
    Makes NLLB's Hindi translation more conversational.

    This intentionally uses lightweight replacements rather
    than another AI/API call so the NLP module remains fully
    local and does not introduce another dependency.
    """

    text = translated_text.strip()

    # -----------------------------------------------------
    # Formal Hindi → conversational Hindi
    # -----------------------------------------------------

    replacements = {

        # Pronouns / addressing
        "आपको": "तुम्हें",
        "आपका": "तुम्हारा",
        "आपकी": "तुम्हारी",
        "आपके": "तुम्हारे",

        # Common formal phrases
        "कृपया": "",
        "चिंता न करें": "टेंशन मत लो",
        "चिंता मत करें": "टेंशन मत लो",

        "कोई चिंता नहीं": "कोई टेंशन नहीं",

        "मुझे प्रसन्नता हुई": "मुझे अच्छा लगा",

        "यह जानकर मुझे प्रसन्नता हुई":
            "ये जानकर मुझे अच्छा लगा",

        "यह सुनकर मुझे प्रसन्नता हुई":
            "ये सुनकर मुझे अच्छा लगा",

        "मैं आपकी सहायता कर सकता हूँ":
            "मैं तुम्हारी मदद कर सकता हूँ",

        "मैं आपकी सहायता कर सकती हूँ":
            "मैं तुम्हारी मदद कर सकती हूँ",

        "मैं आपकी मदद कर सकता हूँ":
            "मैं तुम्हारी मदद कर सकता हूँ",

        "मैं आपकी मदद कर सकती हूँ":
            "मैं तुम्हारी मदद कर सकती हूँ",

        # Formal verbs
        "बताइए": "बताओ",
        "कीजिए": "करो",
        "करिए": "करो",
        "लीजिए": "लो",
        "देखिए": "देखो",
        "सोचिए": "सोचो",
        "समझिए": "समझो",

        # Formal endings
        "कर रहे हैं": "कर रहे हो",
        "कर रही हैं": "कर रही हो",
        "करते हैं": "करते हो",
        "करती हैं": "करती हो",

        # Common formal vocabulary
        "समस्या": "प्रॉब्लम",
        "सहायता": "मदद",
        "आवश्यकता": "ज़रूरत",
        "अत्यंत": "बहुत",
        "प्रसन्न": "खुश",
        "दुखी": "उदास",
        "प्रयास": "कोशिश",
        "विचार": "सोच",
        "जानकारी": "इन्फॉर्मेशन",
        "आरंभ": "शुरुआत",
        "समाप्त": "खत्म",
        "शीघ्र": "जल्दी",
        "वर्तमान": "अभी",
        "परंतु": "लेकिन",
        "क्योंकि": "क्योंकि",
        "अतः": "तो",
    }

    for old, new in replacements.items():

        text = text.replace(
            old,
            new
        )

    # -----------------------------------------------------
    # Remove accidental double spaces
    # -----------------------------------------------------

    while "  " in text:

        text = text.replace(
            "  ",
            " "
        )

    return text.strip()


# =========================================================
# MITRA TRANSLATION
# =========================================================

def translate_for_mitra(
    text: str,
    target_lang: str,
    source_lang: str = None
) -> str:
    """
    Translation specifically for Mitra's responses.

    English → Hindi receives a conversational-Hindi pass.

    All other translations use the normal NLLB pipeline.
    """

    if source_lang is None:

        source_lang = detect_language(
            text
        )

    # -----------------------------------------------------
    # Nothing to translate
    # -----------------------------------------------------

    if source_lang == target_lang:

        return text

    # -----------------------------------------------------
    # English → Hindi
    #
    # This is the important Mitra-specific path.
    # -----------------------------------------------------

    if (
        source_lang == "en"
        and target_lang == "hi"
    ):

        translated = _nllb_translate(
            text,
            target_lang="hi",
            source_lang="en"
        )

        return _make_hindi_conversational(
            translated
        )

    # -----------------------------------------------------
    # Everything else
    # -----------------------------------------------------

    return _nllb_translate(
        text,
        target_lang,
        source_lang
    )


# =========================================================
# PUBLIC TRANSLATE FUNCTION
# =========================================================

def translate(
    text: str,
    target_lang: str,
    source_lang: str = None
) -> str:
    """
    General translation function.

    English → Hindi automatically uses Mitra's
    conversational Hindi style.

    Other language combinations continue using
    the original NLLB translation system.
    """

    return translate_for_mitra(
        text,
        target_lang,
        source_lang
    )


# =========================================================
# EMOTION DETECTION
# =========================================================

def detect_emotion(
    text: str
) -> dict:
    """
    Returns the dominant emotion.

    Example:

        {
            "label": "sadness",
            "score": 0.91
        }

    The emotion classifier is English-only,
    so non-English input is translated first.
    """

    lang = detect_language(
        text
    )

    if lang != "en":

        english_text = translate(
            text,
            target_lang="en",
            source_lang=lang
        )

    else:

        english_text = text

    classifier = (
        _get_emotion_classifier()
    )

    result = classifier(
        english_text
    )[0][0]

    return {
        "label": result["label"],
        "score": round(
            result["score"],
            3
        )
    }


# =========================================================
# QUICK MANUAL TEST
# =========================================================

if __name__ == "__main__":

    samples = [

        "I failed my exam today.",

        "Mujhe aaj bahut bura lag raha hai.",

        "Estoy muy feliz hoy.",

        "I am really happy to hear that you are doing well.",

        "Please don't worry, everything will be okay.",

    ]

    for sample in samples:

        print(
            "----------------------------------------"
        )

        print(
            f"Text: {sample}"
        )

        lang = detect_language(
            sample
        )

        print(
            f"Detected language: {lang}"
        )

        english = translate(
            sample,
            target_lang="en",
            source_lang=lang
        )

        print(
            f"English: {english}"
        )

        # -------------------------------------------------
        # Demonstrate Mitra's Hindi output
        # -------------------------------------------------

        if lang == "en":

            hindi = translate(
                sample,
                target_lang="hi",
                source_lang="en"
            )

            print(
                f"Mitra Hindi: {hindi}"
            )

        emotion = detect_emotion(
            sample
        )

        print(
            f"Emotion: {emotion}"
        )

        print()
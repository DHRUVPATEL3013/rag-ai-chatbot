# """
# Language detection — Phase 2. Tags chunks at ingestion time and
# incoming queries at chat time.
# """


# def detect_language(text: str) -> str:
#     """
#     TODO: Use langdetect.detect(text) (or lingua-language-detector for
#     better short-text accuracy). Return an ISO code: "en", "es", or "fr".

#     Handle failure gracefully — detection on very short strings can raise
#     an exception or return an unsupported language. Decide a sensible
#     default (e.g. "en") for that case.
#     """
#     raise NotImplementedError








from langdetect import detect


SUPPORTED_LANGUAGES = {"en", "es", "fr"}


def detect_language(text: str) -> str:
    """
    Detect whether the text is English, Spanish, or French.

    Defaults to English when detection fails or returns
    an unsupported language.
    """

    if not text or not text.strip():
        return "en"

    try:
        language = detect(text)

        if language in SUPPORTED_LANGUAGES:
            return language

    except Exception:
        pass

    return "en"
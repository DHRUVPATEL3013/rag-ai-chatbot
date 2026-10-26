# """
# PII detection using Microsoft Presidio.

# This module is responsible for detecting sensitive information
# before a user question is stored or sent for processing.
# """

# from presidio_analyzer import AnalyzerEngine


# # Create the analyzer once when the application starts.
# analyzer = AnalyzerEngine()


# # PII types that we currently consider sensitive.
# BLOCKED_ENTITIES = [
#     "EMAIL_ADDRESS",
#     "PHONE_NUMBER",
#     "CREDIT_CARD",
#     "IBAN_CODE",
#     "IP_ADDRESS",
# ]




# MAX_WORDS = 1000
# MAX_CHARACTERS = 10000


# def validate_question(text: str) -> tuple[bool, str]:
#     """
#     Validate a user's question before it enters
#     the chatbot/RAG pipeline.
#     """

#     # 1. Empty / None
#     if not text:
#         return False, "Question cannot be empty."

#     # 2. Only spaces / whitespace
#     if not text.strip():
#         return False, "Question cannot contain only spaces."

#     # 3. Character limit
#     if len(text) > MAX_CHARACTERS:
#         return False, (
#             f"Question is too long. "
#             f"Maximum allowed length is {MAX_CHARACTERS} characters."
#         )

#     # 4. Word limit
#     word_count = len(text.split())

#     if word_count > MAX_WORDS:
#         return False, (
#             f"Question is too long. "
#             f"Maximum allowed length is {MAX_WORDS} words."
#         )

#     # 5. PII detection
#     results = analyzer.analyze(
#         text=text,
#         language="en",
#         entities=BLOCKED_ENTITIES,
#     )

#     if results:
#         detected = list(
#             dict.fromkeys(
#                 result.entity_type
#                 for result in results
#             )
#         )

#         return False, (
#             "Question contains sensitive information. "
#             "Please remove personal or sensitive information "
#             "and try again."
#         )

#     return True, ""



# def detect_pii(text: str) -> list[str]:
#     """
#     Detect sensitive information in the supplied text.

#     Returns a list of detected entity types.

#     Example:

#         "My email is john@gmail.com"

#     returns:

#         ["EMAIL_ADDRESS"]
#     """

#     if not text or not text.strip():
#         return []

#     results = analyzer.analyze(
#         text=text,
#         language="en",
#         entities=BLOCKED_ENTITIES,
#     )

#     return list(
#         dict.fromkeys(
#             result.entity_type
#             for result in results
#         )
#     )


# def contains_pii(text: str) -> bool:
#     """
#     Return True if the text contains blocked PII.
#     """

#     return bool(detect_pii(text))







# =========================================================================================

"""
PII detection and protection using Microsoft Presidio.

PII is detected dynamically and replaced with temporary tokens
before content is sent to the LLM.

The same PII map can be shared across:
- user question
- conversation history
- retrieved context

This keeps the same sensitive value represented by the same token.
"""

from presidio_analyzer import AnalyzerEngine


# ---------------------------------------------------------
# Analyzer
# ---------------------------------------------------------

analyzer = AnalyzerEngine()


# PII types considered sensitive.
BLOCKED_ENTITIES = [
    "EMAIL_ADDRESS",
    "PHONE_NUMBER",
    "CREDIT_CARD",
    "IBAN_CODE",
    "IP_ADDRESS",
]


MAX_WORDS = 1000
MAX_CHARACTERS = 10000


# ---------------------------------------------------------
# Basic question validation
# ---------------------------------------------------------

def validate_question(text: str) -> tuple[bool, str]:
    """
    Validate basic question requirements.

    PII does NOT block the question anymore.
    """

    if not text:
        return False, "Question cannot be empty."

    if not text.strip():
        return False, "Question cannot contain only spaces."

    if len(text) > MAX_CHARACTERS:
        return False, (
            f"Question is too long. "
            f"Maximum allowed length is {MAX_CHARACTERS} characters."
        )

    word_count = len(text.split())

    if word_count > MAX_WORDS:
        return False, (
            f"Question is too long. "
            f"Maximum allowed length is {MAX_WORDS} words."
        )

    return True, ""


# ---------------------------------------------------------
# PII detection
# ---------------------------------------------------------

def detect_pii(text: str) -> list[str]:
    """
    Return detected PII entity types.
    """

    if not text or not text.strip():
        return []

    results = analyzer.analyze(
        text=text,
        language="en",
        entities=BLOCKED_ENTITIES,
    )

    return list(
        dict.fromkeys(
            result.entity_type
            for result in results
        )
    )


def contains_pii(text: str) -> bool:
    """
    Return True if text contains PII.
    """

    return bool(detect_pii(text))


# ---------------------------------------------------------
# Sanitize using shared PII map
# ---------------------------------------------------------

def sanitize_for_llm(
    text: str,
    pii_map: dict[str, str] | None = None,
) -> tuple[str, dict[str, str]]:
    """
    Replace PII values with dynamic tokens.

    A shared pii_map can be supplied so multiple pieces
    of text use the same tokens.

    Example:

        Question:
            What is the email of john@gmail.com?

        Context:
            john@gmail.com is the employee email.

        LLM sees:

            What is the email of <PII_EMAIL_ADDRESS_1>?

            <PII_EMAIL_ADDRESS_1> is the employee email.
    """

    if not text or not text.strip():
        return text, pii_map or {}

    if pii_map is None:
        pii_map = {}

    # Reverse mapping lets us reuse an existing token
    # when the same sensitive value appears again.
    value_to_token = {
        value: token
        for token, value in pii_map.items()
    }

    # Find next token number for each entity type.
    counters = {}

    for token in pii_map:
        # Example:
        # <PII_EMAIL_ADDRESS_2>
        if token.startswith("<PII_") and token.endswith(">"):
            inside = token[5:-1]

            parts = inside.rsplit("_", 1)

            if len(parts) == 2:
                entity_type, number = parts

                try:
                    number = int(number)

                    counters[entity_type] = max(
                        counters.get(entity_type, 0),
                        number,
                    )
                except ValueError:
                    pass

    results = analyzer.analyze(
        text=text,
        language="en",
        entities=BLOCKED_ENTITIES,
    )

    if not results:
        return text, pii_map

    # Process from right to left so character positions
    # remain valid while replacing text.
    results = sorted(
        results,
        key=lambda result: result.start,
        reverse=True,
    )

    sanitized_text = text

    for result in results:

        entity_type = result.entity_type

        original_value = text[
            result.start:result.end
        ]

        # -------------------------------------------------
        # Reuse token if this exact value was already seen
        # -------------------------------------------------

        token = value_to_token.get(original_value)

        if token is None:

            counters[entity_type] = (
                counters.get(entity_type, 0) + 1
            )

            token = (
                f"<PII_{entity_type}_"
                f"{counters[entity_type]}>"
            )

            pii_map[token] = original_value

            value_to_token[original_value] = token

        # -------------------------------------------------
        # Replace value with token
        # -------------------------------------------------

        sanitized_text = (
            sanitized_text[:result.start]
            + token
            + sanitized_text[result.end:]
        )

    return sanitized_text, pii_map


# ---------------------------------------------------------
# Restore PII
# ---------------------------------------------------------

def restore_pii(
    text: str,
    pii_map: dict[str, str],
) -> str:
    """
    Restore original PII values after LLM generation.
    """

    if not text or not pii_map:
        return text

    restored_text = text

    for token, original_value in pii_map.items():
        restored_text = restored_text.replace(
            token,
            original_value,
        )

    return restored_text
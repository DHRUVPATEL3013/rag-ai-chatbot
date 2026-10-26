"""
External AI fallback — Phase 4.
"""


def call_external_ai(query: str, language: str) -> str:
    """
    TODO: Call ChatGroq directly with ONLY the raw user query — never
    pass retrieved internal document chunks here (see the confidentiality
    note in the plan doc: the fallback replaces RAG, it doesn't extend it).
    Instruct the model to answer in `language`.
    """
    raise NotImplementedError


def log_unanswered(query: str, language: str, ai_answer: str):
    """
    TODO: Insert a row into the review_queue table (see db/models.py)
    so an admin can review it in Phase 5.
    """
    raise NotImplementedError

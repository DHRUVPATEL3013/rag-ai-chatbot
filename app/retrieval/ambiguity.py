
import re 
"""
Detect queries that are too short or ambiguous to answer reliably.
"""


def is_ambiguous_query(query: str) -> bool:
    """
    Return True when the query is too short or lacks enough
    meaningful information to safely answer.

    This is intentionally conservative.
    """

    query = query.strip()

    if not query:
        return True


    if not re.search(r"[a-zA-Z0-9]",query):
        return True
    

    text=re.sub(r"\s+","",query)

    if text.isdigit():
        return True

    if re.fullmatch(r"[a-zA-Z0-9]+",text):
        letters = re.findall(r"[a-zA-Z]", text)
        digits = re.findall(r"[0-9]", text)

        if len(text) >=15 and letters and digits and " " not in query:
            return True
        if len(text) >= 20 and not digits:
            return True

    # Very short queries are often incomplete follow-ups.
    words = query.split()

    if len(words) <= 2:
        # These are meaningful standalone queries.
        allowed_short_queries = {
            "annual leave",
            "medical leave",
            "casual leave",
            "remote work",
            "employee benefits",
            "expense policy",
            "attendance policy",
        }
        
        normalized = " ".join(words).lower().strip("?.!")

        if normalized in allowed_short_queries:
            return False

        # Pronoun/reference-heavy short queries are ambiguous.
        ambiguous_words = {
            "and",
            "what",
            "which",
            "how",
            "why",
            "that",
            "this",
            "those",
            "these",
            "it",
            "them",
        }

        if any(word.lower().strip("?.!,") in ambiguous_words
               for word in words):
            return True

    return False
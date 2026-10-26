# """
# Confidence scoring — Phase 4 fallback trigger.
# """


# def is_low_confidence(retrieved_docs_with_scores: list, threshold: float = None) -> bool:
#     """
#     TODO: Chroma's similarity_search_with_score() returns (Document, score)
#     pairs. Compare the best score against settings.CONFIDENCE_THRESHOLD.

#     Important: check which distance metric your Chroma collection uses —
#     for the default (L2 distance), LOWER means MORE similar, which is the
#     opposite of a typical "confidence" score. Get this comparison direction
#     right before wiring it into the fallback branch, or you'll trigger the
#     fallback on your best matches instead of your worst ones.
#     """
#     raise NotImplementedError




"""
Confidence scoring — Phase 4 fallback trigger.
"""

# from app.config import settings
# from app.ingestion.embed_store import get_vectorstore


# def is_low_confidence(
#     retrieved_docs_with_scores: list,
#     threshold: float = None,
# ) -> bool:
#     """
#     Check whether the best retrieved document has a high distance
#     and should therefore be considered low confidence.

#     Chroma's default L2 distance:
#         lower score = more similar
#         higher score = less similar
#     """

#     if not retrieved_docs_with_scores:
#         return True

#     if threshold is None:
#         threshold = settings.CONFIDENCE_THRESHOLD

#     best_score = min(
#         score for _, score in retrieved_docs_with_scores
#     )

#     return best_score > threshold

"""
Confidence scoring — Phase 4 fallback trigger.
"""

from app.config import settings


def is_low_confidence(
    retrieved_docs_with_scores: list,
    threshold: float = None,
) -> bool:
    """
    Check whether the best retrieved document is too far away.

    Chroma returns L2 distance scores:
        lower score  = more similar
        higher score = less similar
    """

    if not retrieved_docs_with_scores:
        return True

    if threshold is None:
        threshold = settings.CONFIDENCE_THRESHOLD

    best_score = min(
        score
        for _, score in retrieved_docs_with_scores
    )

    print(best_score)

    return best_score > threshold


# def filter_relevant_documents(
#     retrieved_docs_with_scores: list,
#     threshold: float = None,
# ) -> list:
#     """Keep only documents within the relevance distance threshold."""

#     if threshold is None:
#         threshold = settings.RELEVANCE_THRESHOLD

#     return [
#         (document, score)
#         for document, score in retrieved_docs_with_scores
#         if score <= threshold
#     ]



def filter_relevant_documents(
    retrieved_docs_with_scores: list,
    threshold: float = None,
) -> list:
    """Keep relevant documents and remove duplicate content."""

    if threshold is None:
        threshold = settings.RELEVANCE_THRESHOLD

    for document,score in retrieved_docs_with_scores:
        print(f"SCORE ---- {score}")

    filtered = [
        (document, score)
        for document, score in retrieved_docs_with_scores
        if score <= threshold
    ]

    unique = []
    seen_content = set()

    for document, score in filtered:
        content = " ".join(document.page_content.split())

        if content in seen_content:
            continue

        seen_content.add(content)
        unique.append((document, score))

    print(f"UINQUE ---- {unique}")

    return unique






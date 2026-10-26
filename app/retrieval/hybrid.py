"""
Hybrid retrieval — Phase 4.

Combines:
1. Semantic search using Chroma embeddings
2. Keyword search using BM25
3. Reciprocal Rank Fusion (RRF)
4. Source diversity limiting
"""

from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
import re
from app.ingestion.embed_store import get_vectorstore

def tokenize(text: str) -> list[str]:
    return re.findall(
        r"[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*",
        text.lower(),
    )

def keyword_search(query: str, k: int = 5):
    vectorstore = get_vectorstore()
    collection = vectorstore._collection

    total = collection.count()

    documents = []
    metadatas = []

    batch_size = 500

    for offset in range(0, total, batch_size):
        data = collection.get(
            offset=offset,
            limit=batch_size,
            include=["documents", "metadatas"],
        )

        documents.extend(data["documents"])
        metadatas.extend(data["metadatas"])

    query_lower = query.lower()

    # Exact employee/pet ID lookup
    ids = re.findall(
        r"\b(?:pet|emp)-\d{6}\b",
        query_lower,
    )

    exact_results = []

    if ids:
        for document, metadata in zip(documents, metadatas):
            document_lower = document.lower()

            if any(pet_id in document_lower for pet_id in ids):
                exact_results.append(
                    {
                        "score": 1000,
                        "content": document,
                        "metadata": metadata,
                    }
                )

        if exact_results:
            return exact_results[:k]

    # Normal keyword matching
    query_tokens = tokenize(query)

    scored = []

    for document, metadata in zip(documents, metadatas):
        document_tokens = tokenize(document)

        score = sum(
            1
            for token in query_tokens
            if token in document_tokens
        )

        if score > 0:
            scored.append(
                {
                    "score": score,
                    "content": document,
                    "metadata": metadata,
                }
            )

    scored.sort(
        key=lambda x: x["score"],
        reverse=True,
    )

    return scored[:k]

# def keyword_search(query: str, k: int = 5):
#     """
#     Search documents using BM25 keyword matching.

#     BM25 is useful when the query contains exact terms that
#     semantic search may fail to retrieve accurately.
#     """

#     vectorstore = get_vectorstore()

#     data = vectorstore._collection.get(
#         include=["documents", "metadatas"]
#     )

#     documents = data["documents"]
#     metadatas = data["metadatas"]

#     if not documents:
#         return []

#     # Tokenize documents
#     tokenized_documents = [
#         document.lower().split()
#         for document in documents
#     ]

#     bm25 = BM25Okapi(tokenized_documents)

#     # Tokenize query
#     query_tokens = query.lower().split()

#     scores = bm25.get_scores(query_tokens)

#     # Rank highest BM25 score first
#     ranked_indexes = sorted(
#         range(len(scores)),
#         key=lambda i: scores[i],
#         reverse=True,
#     )

#     results = []

#     for index in ranked_indexes[:k]:
#         results.append(
#             {
#                 "content": documents[index],
#                 "metadata": metadatas[index],
#                 "score": float(scores[index]),
#             }
#         )

#     return results


def hybrid_search(query: str, k: int = 5):
    """
    Combine semantic and keyword search using Reciprocal Rank Fusion.

    Semantic search is good for understanding meaning.

    BM25 keyword search is good for exact terms such as:
        - visitor
        - reception
        - transport allowance
        - 100 euros
        - probation

    RRF combines the rankings from both approaches.
    """
    candidate_k = 20

    vectorstore = get_vectorstore()

    # =========================================================
    # 1. Semantic search
    # =========================================================

    # semantic_results = vectorstore.similarity_search_with_score(
    #     query,
    #     k=k,
    # )
    semantic_results = vectorstore.similarity_search_with_score(
        query,
        k=candidate_k,
    )

    # =========================================================
    # 2. Keyword search
    # =========================================================

    # keyword_results = keyword_search(
    #     query,
    #     k=k,
    # )
    keyword_results = keyword_search(
        query,
        k=candidate_k,
    )

    # =========================================================
    # 3. Combine documents
    # =========================================================

    combined = {}

    # ---------------------------------------------------------
    # Add semantic results
    # ---------------------------------------------------------

    for rank, (document, distance) in enumerate(
        semantic_results,
        start=1,
    ):

        key = (
            document.metadata.get("source"),
            document.page_content,
        )

        combined[key] = {
            "document": document,

            # Original Chroma distance
            "semantic_distance": float(distance),

            # Rank in semantic search
            "semantic_rank": rank,

            # Will be filled if BM25 also finds this document
            "keyword_rank": None,

            # RRF scores
            "semantic_score": 0.0,
            "keyword_score": 0.0,
            "combined_score": 0.0,
        }

    # ---------------------------------------------------------
    # Add keyword results
    # ---------------------------------------------------------

    for rank, result in enumerate(
        keyword_results,
        start=1,
    ):

        document = Document(
            page_content=result["content"],
            metadata=result["metadata"],
        )

        key = (
            document.metadata.get("source"),
            document.page_content,
        )

        if key in combined:

            combined[key]["keyword_rank"] = rank

        else:

            combined[key] = {
                "document": document,

                "semantic_distance": None,

                "semantic_rank": None,

                "keyword_rank": rank,

                "semantic_score": 0.0,
                "keyword_score": 0.0,
                "combined_score": 0.0,
            }

    # =========================================================
    # 4. Reciprocal Rank Fusion
    # =========================================================

    RRF_K = 60

    for result in combined.values():

        semantic_rank = result["semantic_rank"]
        keyword_rank = result["keyword_rank"]

        # Semantic RRF score
        if semantic_rank is not None:

            semantic_rrf = (
                1 / (RRF_K + semantic_rank)
            )

        else:

            semantic_rrf = 0.0

        # Keyword RRF score
        if keyword_rank is not None:

            keyword_rrf = (
                1 / (RRF_K + keyword_rank)
            )

        else:

            keyword_rrf = 0.0

        result["semantic_score"] = semantic_rrf
        result["keyword_score"] = keyword_rrf

        result["combined_score"] = (
            semantic_rrf + keyword_rrf
        )

    # =========================================================
    # 5. Sort by combined RRF score
    # =========================================================

    results = list(combined.values())

    results.sort(
        key=lambda result: result["combined_score"],
        reverse=True,
    )

    # =========================================================
    # 6. Limit duplicate sources
    # =========================================================

    final_results = []

    source_counts = {}

    MAX_PER_SOURCE = 2

    for result in results:

        source = result["document"].metadata.get(
            "source",
            "unknown",
        )

        count = source_counts.get(
            source,
            0,
        )

        # Avoid returning too many chunks from
        # the same document.
        if count >= MAX_PER_SOURCE:
            continue

        final_results.append(result)

        source_counts[source] = count + 1

        if len(final_results) >= k:
            break

    return final_results
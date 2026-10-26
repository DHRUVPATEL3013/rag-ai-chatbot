"""
RAG retrieval — semantic + BM25 + CrossEncoder reranking.
"""

import hashlib
import re
from functools import lru_cache

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder

from app.ingestion.embed_store import get_vectorstore


# ============================================================
# Configuration
# ============================================================

SEMANTIC_K = 30
BM25_K = 30
RRF_K = 60
RERANK_K = 15

RERANKER_MODEL = (
    "hasankursun/reranker-Multilingual-MiniLM-L12-H384-msmarco-mse"
)


# ============================================================
# Existing Chroma retriever
# ============================================================

def get_retriever(
    category: str = None,
    language: str = None,
    k: int = 4,
):
    """
    Build a Chroma retriever with optional metadata filtering.
    """

    vectorstore = get_vectorstore()

    search_kwargs = {
        "k": k,
    }

    filters = {}

    if category:
        filters["category"] = category

    if language:
        filters["language"] = language

    if filters:
        if len(filters) == 1:
            search_kwargs["filter"] = filters
        else:
            search_kwargs["filter"] = {
                "$and": [
                    {"category": category},
                    {"language": language},
                ]
            }

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            **search_kwargs,
            "fetch_k": 20,
        },
    )


# ============================================================
# Helpers
# ============================================================

def _normalize_text(text: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        (text or "").strip().lower(),
    )


def _tokenize(text: str) -> list[str]:
    return re.findall(
        r"\w+(?:-\w+)*",
        _normalize_text(text),
    )


def _stable_key(document: Document) -> str:
    """
    Create a stable key for deduplicating the same chunk
    returned by semantic and BM25 retrieval.
    """

    metadata = document.metadata or {}

    chunk_id = (
        metadata.get("id")
        or metadata.get("chunk_id")
    )

    if chunk_id:
        return f"id:{chunk_id}"

    source = (
        metadata.get("source")
        or metadata.get("filename")
        or ""
    )

    page = (
        metadata.get("page")
        or metadata.get("page_number")
        or ""
    )

    text = _normalize_text(
        document.page_content
    )

    raw = f"{source}|{page}|{text}"

    return "hash:" + hashlib.sha1(
        raw.encode("utf-8")
    ).hexdigest()


# ============================================================
# Cached BM25 index
# ============================================================

@lru_cache(maxsize=1)
def _get_bm25_index():
    """
    Load all Chroma chunks once and build the BM25 index.

    The cache prevents rebuilding the BM25 index for every query.
    """

    vectorstore = get_vectorstore()
    collection = vectorstore._collection

    total = collection.count()

    if total==0:
        print("[BM25] No documents found in ChromaDB.")
        return None,[]

    documents = []

    batch_size = 500

    print("\n" + "=" * 60)
    print("[BM25] Building BM25 index")
    print("=" * 60)
    print(f"[BM25] Total Chroma chunks: {total:,}")

    for offset in range(0, total, batch_size):

        data = collection.get(
            offset=offset,
            limit=batch_size,
            include=[
                "documents",
                "metadatas",
            ],
        )

        batch_documents = data.get(
            "documents",
            [],
        )

        batch_metadatas = data.get(
            "metadatas",
            [],
        )

        for text, metadata in zip(
            batch_documents,
            batch_metadatas,
        ):
            documents.append(
                Document(
                    page_content=text,
                    metadata=metadata or {},
                )
            )

        print(
            f"[BM25] Loaded "
            f"{min(offset + batch_size, total):,}"
            f"/{total:,}",
            end="\r",
        )

    print()

    tokenized_documents = [
        _tokenize(document.page_content)
        for document in documents
    ]

    bm25 = BM25Okapi(
        tokenized_documents
    )

    print(
        f"[BM25] Index ready: "
        f"{len(documents):,} documents"
    )

    print("=" * 60)

    return bm25, documents


# ============================================================
# Cached CrossEncoder
# ============================================================

@lru_cache(maxsize=1)
def _get_reranker():
    """
    Load the CrossEncoder once per application process.
    """

    print("\n" + "=" * 60)
    print("[RERANKER] Loading CrossEncoder")
    print("=" * 60)
    print(
        f"[RERANKER] Model: "
        f"{RERANKER_MODEL}"
    )

    reranker = CrossEncoder(
        RERANKER_MODEL
    )

    print("[RERANKER] Model ready")
    print("=" * 60)

    return reranker


# ============================================================
# Hybrid retrieval + reranking
# ============================================================

def retrieve_with_scores(
    query: str,
    k: int = 10,
):
    """
    Retrieve documents using:

        1. Chroma semantic search
        2. BM25 keyword search
        3. Reciprocal Rank Fusion
        4. CrossEncoder reranking

    IMPORTANT:
    The returned score remains the ORIGINAL Chroma distance.

    This preserves compatibility with the existing confidence
    and relevance filtering code.
    """

    vectorstore = get_vectorstore()
    if vectorstore._collection.count() == 0:
        return []

    # --------------------------------------------------------
    # 1. Semantic retrieval
    # --------------------------------------------------------

    semantic_results = (
        vectorstore.similarity_search_with_score(
            query,
            k=SEMANTIC_K,
        )
    )

    semantic_map = {}

    for rank, (
        document,
        distance,
    ) in enumerate(
        semantic_results,
        start=1,
    ):

        key = _stable_key(
            document
        )

        semantic_map[key] = {
            "document": document,
            "semantic_rank": rank,
            "semantic_distance": float(
                distance
            ),
            "bm25_rank": None,
            "bm25_score": None,
        }

    # --------------------------------------------------------
    # 2. BM25 retrieval
    # --------------------------------------------------------

    bm25, all_documents = (
        _get_bm25_index()
    )

    query_tokens = _tokenize(
        query
    )

    bm25_scores = bm25.get_scores(
        query_tokens
    )

    ranked_indexes = sorted(
        range(len(bm25_scores)),
        key=lambda index: bm25_scores[index],
        reverse=True,
    )[:BM25_K]

    bm25_map = {}

    for rank, index in enumerate(
        ranked_indexes,
        start=1,
    ):

        document = all_documents[index]

        key = _stable_key(
            document
        )

        bm25_map[key] = {
            "document": document,
            "bm25_rank": rank,
            "bm25_score": float(
                bm25_scores[index]
            ),
        }

    # --------------------------------------------------------
    # 3. Merge + deduplicate
    # --------------------------------------------------------

    combined = {}

    for key, item in semantic_map.items():

        combined[key] = {
            "document": item["document"],
            "semantic_rank": item[
                "semantic_rank"
            ],
            "semantic_distance": item[
                "semantic_distance"
            ],
            "bm25_rank": None,
            "bm25_score": None,
        }

    for key, item in bm25_map.items():

        if key not in combined:

            combined[key] = {
                "document": item["document"],
                "semantic_rank": None,
                "semantic_distance": None,
                "bm25_rank": item[
                    "bm25_rank"
                ],
                "bm25_score": item[
                    "bm25_score"
                ],
            }

        else:

            combined[key][
                "bm25_rank"
            ] = item["bm25_rank"]

            combined[key][
                "bm25_score"
            ] = item["bm25_score"]

    # --------------------------------------------------------
    # 4. Reciprocal Rank Fusion
    # --------------------------------------------------------

    for item in combined.values():

        rrf_score = 0.0

        semantic_rank = item[
            "semantic_rank"
        ]

        bm25_rank = item[
            "bm25_rank"
        ]

        if semantic_rank is not None:

            rrf_score += (
                1.0
                / (
                    RRF_K
                    + semantic_rank
                )
            )

        if bm25_rank is not None:

            rrf_score += (
                1.0
                / (
                    RRF_K
                    + bm25_rank
                )
            )

        item["rrf_score"] = rrf_score

    # --------------------------------------------------------
    # 5. Candidate selection
    # --------------------------------------------------------

    candidates = sorted(
        combined.values(),
        key=lambda item: item[
            "rrf_score"
        ],
        reverse=True,
    )[:RERANK_K]

    if not candidates:
        return []

    # --------------------------------------------------------
    # 6. CrossEncoder reranking
    # --------------------------------------------------------

    reranker = _get_reranker()

    pairs = [
        (
            query,
            item["document"].page_content,
        )
        for item in candidates
    ]

    reranker_scores = reranker.predict(
        pairs
    )

    for item, score in zip(
        candidates,
        reranker_scores,
    ):
        item["reranker_score"] = float(
            score
        )

    candidates.sort(
        key=lambda item: item[
            "reranker_score"
        ],
        reverse=True,
    )

    # --------------------------------------------------------
    # 7. Return existing interface
    # --------------------------------------------------------

    results = []

    for item in candidates[:k]:

        document = item["document"]

        # IMPORTANT:
        # Keep the original Chroma distance.
        # Do NOT return the CrossEncoder score here.
        distance = item[
            "semantic_distance"
        ]

        if distance is None:
            # BM25-only candidate has no Chroma
            # distance. We need a Chroma distance
            # before returning it.
            #
            # Search this specific document through
            # Chroma using its content.
            matching = (
                vectorstore
                .similarity_search_with_score(
                    document.page_content,
                    k=1,
                )
            )

            if matching:
                distance = float(
                    matching[0][1]
                )
            else:
                continue

        results.append(
            (
                document,
                float(distance),
            )
        )

    return results
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from langchain_core.documents import Document

from app.ingestion.embed_store import get_vectorstore


MODEL_NAME = "hasankursun/reranker-Multilingual-MiniLM-L12-H384-msmarco-mse"

QUESTIONS = [
    "How many annual leave days does a full-time employee receive each year?",
    "How many unused annual leave days can be carried into the next year?",
    "How many weeks of parental leave are available to eligible employees?",
    "What is the standard notice period for confirmed employees?",
    "How many days in advance should annual leave normally be requested?",
    "When must carried-over annual leave be used?",
    "How long is the probation period?",
    "How many days do employees have to submit travel expenses?",
    "What is the process for taking sick leave?",
    "What are the obligations when working remotely?",
]


def tokenize(text: str):
    return text.lower().split()


def get_bm25_candidates(query, documents, top_n=20):
    corpus = [tokenize(doc.page_content) for doc in documents]

    bm25 = BM25Okapi(corpus)

    scores = bm25.get_scores(tokenize(query))

    ranked = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    return ranked[:top_n]


def get_semantic_candidates(query, k=20):
    vectorstore = get_vectorstore()

    return vectorstore.similarity_search_with_score(
        query,
        k=k,
    )


def reciprocal_rank_fusion(
    semantic_results,
    bm25_results,
    rrf_k=60,
):
    combined = {}

    def make_key(doc):
        metadata = doc.metadata or {}

        source = (
            metadata.get("source")
            or metadata.get("filename")
            or "unknown"
        )

        return source + "|" + doc.page_content[:200]

    for rank, (doc, distance) in enumerate(
        semantic_results,
        start=1,
    ):
        key = make_key(doc)

        if key not in combined:
            combined[key] = {
                "document": doc,
                "semantic_distance": distance,
                "semantic_rank": rank,
                "bm25_rank": None,
                "rrf_score": 0.0,
            }

        combined[key]["rrf_score"] += 1 / (rrf_k + rank)

    for rank, (doc, bm25_score) in enumerate(
        bm25_results,
        start=1,
    ):
        key = make_key(doc)

        if key not in combined:
            combined[key] = {
                "document": doc,
                "semantic_distance": None,
                "semantic_rank": None,
                "bm25_rank": rank,
                "rrf_score": 0.0,
            }
        else:
            combined[key]["bm25_rank"] = rank

        combined[key]["rrf_score"] += 1 / (rrf_k + rank)

    return sorted(
        combined.values(),
        key=lambda x: x["rrf_score"],
        reverse=True,
    )


def load_documents_in_batches(batch_size=500):
    vectorstore = get_vectorstore()
    collection = vectorstore._collection

    total = collection.count()

    print(f"Total Chroma chunks: {total}")
    print(f"Loading in batches of {batch_size}...")

    documents = []

    for offset in range(0, total, batch_size):
        end = min(offset + batch_size, total)

        print(
            f"Loading {offset + 1}-{end} "
            f"of {total}"
        )

        data = collection.get(
            limit=batch_size,
            offset=offset,
            include=["documents", "metadatas"],
        )

        texts = data.get("documents") or []
        metadatas = data.get("metadatas") or []

        for text, metadata in zip(texts, metadatas):
            documents.append(
                Document(
                    page_content=text,
                    metadata=metadata or {},
                )
            )

    print(f"Documents loaded: {len(documents)}")

    return documents


print("=" * 80)
print("BM25 + SEMANTIC + CROSSENCODER TEST")
print("=" * 80)
print("LLM calls: 0")
print("LLM/API tokens used: 0")
print(f"Reranker: {MODEL_NAME}")
print("=" * 80)


print("\nLoading reranker...")

start = time.perf_counter()

reranker = CrossEncoder(
    MODEL_NAME,
    max_length=512,
)

print(
    f"Reranker loaded in "
    f"{time.perf_counter() - start:.2f}s"
)


print("\nLoading Chroma documents...")

start = time.perf_counter()

documents = load_documents_in_batches(
    batch_size=500,
)

print(
    f"Document loading time: "
    f"{time.perf_counter() - start:.2f}s"
)


print("\nBuilding BM25 index...")

start = time.perf_counter()

corpus = [
    tokenize(doc.page_content)
    for doc in documents
]

bm25 = BM25Okapi(corpus)

print(
    f"BM25 index built in "
    f"{time.perf_counter() - start:.2f}s"
)


for query in QUESTIONS:

    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    # -----------------------------------------------------
    # Semantic retrieval
    # -----------------------------------------------------

    start = time.perf_counter()

    semantic_results = get_semantic_candidates(
        query,
        k=20,
    )

    semantic_time = time.perf_counter() - start

    # -----------------------------------------------------
    # BM25 retrieval
    # -----------------------------------------------------

    start = time.perf_counter()

    scores = bm25.get_scores(
        tokenize(query)
    )

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True,
    )[:20]

    bm25_results = [
        (
            documents[i],
            scores[i],
        )
        for i in ranked_indexes
    ]

    bm25_time = time.perf_counter() - start

    # -----------------------------------------------------
    # RRF
    # -----------------------------------------------------

    fused = reciprocal_rank_fusion(
        semantic_results,
        bm25_results,
    )

    candidates = fused[:15]

    # -----------------------------------------------------
    # CrossEncoder
    # -----------------------------------------------------

    pairs = [
        (
            query,
            item["document"].page_content,
        )
        for item in candidates
    ]

    start = time.perf_counter()

    reranker_scores = reranker.predict(
        pairs,
        show_progress_bar=False,
    )

    rerank_time = time.perf_counter() - start

    for item, score in zip(
        candidates,
        reranker_scores,
    ):
        item["reranker_score"] = float(score)

    candidates.sort(
        key=lambda x: x["reranker_score"],
        reverse=True,
    )

    print(
        f"\nSemantic time: {semantic_time:.3f}s"
        f"\nBM25 time: {bm25_time:.3f}s"
        f"\nReranking time: {rerank_time:.3f}s"
        f"\nSemantic candidates: {len(semantic_results)}"
        f"\nBM25 candidates: {len(bm25_results)}"
        f"\nFinal candidates: {len(candidates)}"
    )

    print("\nTOP RESULTS:")

    for rank, item in enumerate(
        candidates[:10],
        start=1,
    ):
        doc = item["document"]
        metadata = doc.metadata or {}

        source = (
            metadata.get("filename")
            or metadata.get("source")
            or "unknown"
        )

        page = metadata.get("page", "?")

        text = (
            doc.page_content
            .replace("\n", " ")
            .strip()
        )

        if len(text) > 250:
            text = text[:250] + "..."

        print(
            f"\nRank {rank}"
            f"\n  Reranker score: "
            f"{item['reranker_score']:.6f}"
            f"\n  RRF score: "
            f"{item['rrf_score']:.6f}"
            f"\n  Semantic rank: "
            f"{item['semantic_rank']}"
            f"\n  BM25 rank: "
            f"{item['bm25_rank']}"
            f"\n  Semantic distance: "
            f"{item['semantic_distance']}"
            f"\n  Source: {source}"
            f"\n  Page: {page}"
            f"\n  Text: {text}"
        )


print("\n" + "=" * 80)
print("TEST COMPLETE")
print("LLM calls: 0")
print("LLM/API tokens used: 0")
print("=" * 80)
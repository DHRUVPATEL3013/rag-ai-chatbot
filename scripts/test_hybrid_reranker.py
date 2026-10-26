import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from sentence_transformers import CrossEncoder
from app.retrieval.hybrid import hybrid_search


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


print("=" * 80)
print("HYBRID + CROSSENCODER RERANKER TEST")
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

load_time = time.perf_counter() - start
print(f"Reranker loaded in {load_time:.2f}s")


for question in QUESTIONS:
    print("\n" + "=" * 80)
    print(f"QUERY: {question}")
    print("=" * 80)

    start = time.perf_counter()

    # Hybrid retrieval only.
    # This does NOT call the LLM.
    candidates = hybrid_search(question, k=15)

    retrieval_time = time.perf_counter() - start

    if not candidates:
        print("NO CANDIDATES")
        continue

    pairs = []

    for item in candidates:
        doc = item["document"]
        text = doc.page_content

        pairs.append((question, text))

    start = time.perf_counter()

    scores = reranker.predict(
        pairs,
        show_progress_bar=False,
    )

    rerank_time = time.perf_counter() - start

    results = []

    for item, score in zip(candidates, scores):
        results.append(
            {
                "document": item["document"],
                "reranker_score": float(score),
                "semantic_rank": item.get("semantic_rank"),
                "keyword_rank": item.get("keyword_rank"),
                "combined_score": item.get("combined_score"),
                "semantic_distance": item.get("semantic_distance"),
            }
        )

    results.sort(
        key=lambda x: x["reranker_score"],
        reverse=True,
    )

    print(f"\nHybrid candidates: {len(candidates)}")
    print(f"Hybrid retrieval time: {retrieval_time:.3f}s")
    print(f"Reranking time: {rerank_time:.3f}s")

    print("\nTOP RERANKED RESULTS:")

    for rank, item in enumerate(results[:10], start=1):
        doc = item["document"]
        metadata = doc.metadata or {}

        source = (
            metadata.get("filename")
            or metadata.get("source")
            or "unknown"
        )

        page = metadata.get("page", "?")

        text = doc.page_content.replace("\n", " ").strip()

        if len(text) > 250:
            text = text[:250] + "..."

        print(
            f"\nRank {rank}"
            f"\n  Reranker score: {item['reranker_score']:.6f}"
            f"\n  Semantic rank: {item['semantic_rank']}"
            f"\n  Keyword rank: {item['keyword_rank']}"
            f"\n  Hybrid score: {item['combined_score']:.6f}"
            f"\n  Semantic distance: {item['semantic_distance']}"
            f"\n  Source: {source}"
            f"\n  Page: {page}"
            f"\n  Text: {text}"
        )


print("\n" + "=" * 80)
print("TEST COMPLETE")
print("LLM calls: 0")
print("LLM/API tokens used: 0")
print("=" * 80)
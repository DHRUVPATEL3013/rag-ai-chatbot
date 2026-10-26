
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.retriever import retrieve_with_scores
from sentence_transformers import CrossEncoder

MODEL_NAME = "hasankursun/reranker-Multilingual-MiniLM-L12-H384-msmarco-mse"

QUESTIONS = [
    "How many annual leave days does a full-time employee receive each year?",
    "How far in advance should planned annual leave normally be requested?",
    "How many unused annual leave days can be carried into the next year?",
    "When must carried-forward annual leave normally be used?",
    "How many weeks of parental leave are available to eligible employees?",
    "How long is the standard probation period?",
    "How long is the standard notice period for confirmed employees?",
    "When should business travel expenses normally be submitted?",
    "What should an employee do when they are unable to work because of illness?",
    "Does working remotely change normal leave or attendance obligations?",
]

def main():
    print("=" * 100)
    print("REAL RETRIEVAL + RERANKER TEST")
    print("=" * 100)
    print("LLM calls: 0")
    print("LLM/API tokens used: 0")
    print("")

    print(f"Loading reranker: {MODEL_NAME}")
    model = CrossEncoder(MODEL_NAME)

    for number, query in enumerate(QUESTIONS, start=1):
        print("\n" + "=" * 100)
        print(f"QUESTION {number}: {query}")
        print("=" * 100)

        print("Retrieving top 15 from Chroma...")
        results = retrieve_with_scores(query, k=15)
        print(f"Retrieved: {len(results)}")

        pairs = [(query, doc.page_content) for doc, _ in results]

        start = time.perf_counter()
        scores = model.predict(pairs)
        elapsed = time.perf_counter() - start

        ranked = sorted(
            zip(scores, results),
            key=lambda item: item[0],
            reverse=True,
        )

        print(f"Reranking time: {elapsed:.3f}s")
        print("\nTOP 5 AFTER RERANKING:")

        for rank, (reranker_score, (doc, chroma_distance)) in enumerate(ranked[:5], start=1):
            source = doc.metadata.get("source")
            page = doc.metadata.get("page")
            print(
                f"\nRANK {rank} | RERANKER={reranker_score:.6f}"
                f" | CHROMA_DISTANCE={chroma_distance:.6f}"
                f" | SOURCE={source} | PAGE={page}"
            )
            print(doc.page_content[:700].replace("\n", " "))

if __name__ == "__main__":
    main()

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.retriever import retrieve_with_scores


QUESTIONS = [
    "How many annual leave days does a full-time employee receive each year?",
    "How many unused annual leave days can be carried into the next year?",
    "How many weeks of parental leave are available to eligible employees?",
    "How long is the standard notice period for confirmed employees?",
]


for query in QUESTIONS:
    print("\n" + "=" * 100)
    print("QUESTION:", query)
    print("=" * 100)

    results = retrieve_with_scores(query, k=50)

    for rank, (doc, distance) in enumerate(results, start=1):
        source = doc.metadata.get("source")
        page = doc.metadata.get("page")

        print(
            f"\nRANK {rank} | "
            f"DISTANCE={distance:.6f} | "
            f"SOURCE={source} | "
            f"PAGE={page}"
        )

        print(doc.page_content[:300].replace("\n", " "))
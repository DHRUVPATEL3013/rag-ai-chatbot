import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid import keyword_search


queries = [
    "What breed is PET-000123?",
    "What is the temperament of Luna-371?",
]

for query in queries:
    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = keyword_search(query, k=10)

    for rank, result in enumerate(results, start=1):
        print(f"\n--- RESULT {rank} ---")
        print("BM25 score:", result["score"])
        print("Metadata:", result["metadata"])
        print("Content:")
        print(result["content"][:1200])

        if "PET-000123" in result["content"]:
            print(">>> FOUND PET-000123 <<<")

        if "Luna-371" in result["content"]:
            print(">>> FOUND LUNA-371 <<<")
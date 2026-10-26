import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.hybrid import hybrid_search


queries = [
    "What breed is PET-000123?",
    "What is the temperament of Luna-371?",
]


for query in queries:
    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = hybrid_search(query, k=10)

    print("\nNUMBER OF RESULTS:", len(results))

    for rank, result in enumerate(results, start=1):
        print(f"\n--- RESULT {rank} ---")
        print("TYPE:", type(result))
        print("RAW RESULT:")
        print(result)
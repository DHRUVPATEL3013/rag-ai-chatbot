import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


def test_query(query: str, k: int = 10):
    vectorstore = get_vectorstore()

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = vectorstore.similarity_search_with_score(
        query,
        k=k,
    )

    for rank, (doc, distance) in enumerate(results, start=1):
        print(f"\n--- RESULT {rank} ---")
        print(f"Distance: {distance}")
        print(f"Source: {doc.metadata.get('source')}")
        print(f"Metadata: {doc.metadata}")
        print("Content:")
        print(doc.page_content[:1200])

        if "Luna-371" in doc.page_content:
            print(">>> FOUND LUNA-371 <<<")

        if "PET-000123" in doc.page_content:
            print(">>> FOUND PET-000123 <<<")


if __name__ == "__main__":
    test_query("What is the temperament of Luna-371?", k=10)
    test_query("What breed is PET-000123?", k=10)
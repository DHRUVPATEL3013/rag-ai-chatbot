import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


queries = [
    # PET-000123
    "PET-000123",
    "What breed is PET-000123?",
    "What is the breed of PET-000123?", 
    "Tell me the breed of Max-123",

    # Luna-371
    "Luna-371",
    "What is the temperament of Luna-371?",
    "What is Luna-371's temperament?",
    "Tell me about the temperament of Luna-371",
]


vectorstore = get_vectorstore()


for query in queries:
    print("\n" + "=" * 90)
    print("QUERY:", query)
    print("=" * 90)

    results = vectorstore.similarity_search_with_score(
        query,
        k=10,
    )

    found_pet = False
    found_luna = False

    for rank, (doc, distance) in enumerate(results, start=1):
        content = doc.page_content

        print(f"\n--- RESULT {rank} ---")
        print("Distance:", distance)
        print("Page:", doc.metadata.get("page_label"))
        print("Source:", doc.metadata.get("filename"))

        # Show only the beginning to keep output manageable
        print(content[:500].replace("\n", " "))

        if "PET-000123" in content:
            print(">>> FOUND PET-000123 <<<")
            found_pet = True

        if "Luna-371" in content:
            print(">>> FOUND LUNA-371 <<<")
            found_luna = True

    print("\nFOUND PET-000123:", found_pet)
    print("FOUND LUNA-371:", found_luna)
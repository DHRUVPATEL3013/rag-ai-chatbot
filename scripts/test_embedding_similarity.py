import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


vectorstore = get_vectorstore()
collection = vectorstore._collection


tests = [
    ("PET-000123", "PET-000123"),
    ("Luna-371", "Luna-371"),
]


for label, query in tests:

    print("\n" + "=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    results = vectorstore.similarity_search_with_score(
        query,
        k=50,
    )

    found = False

    for rank, (doc, distance) in enumerate(results, start=1):

        content = doc.page_content

        if label.lower() in content.lower():

            print("\nFOUND TARGET")
            print("Rank:", rank)
            print("Distance:", distance)
            print("Metadata:", doc.metadata)
            print("\nContent:")
            print(content)

            found = True
            break

    if not found:
        print("\nTARGET NOT FOUND IN TOP 50")

        print("\nTop 10 results:")

        for rank, (doc, distance) in enumerate(results[:10], start=1):

            print(
                f"\n{rank}. distance={distance}"
            )

            print(
                doc.page_content[:300]
                .replace("\n", " ")
            )
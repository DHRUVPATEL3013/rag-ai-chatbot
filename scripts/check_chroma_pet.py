import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


vectorstore = get_vectorstore()
collection = vectorstore._collection

total = collection.count()

print("=" * 80)
print("CHROMA COLLECTION CHECK")
print("=" * 80)
print("Total chunks:", total)

target = "Luna-371"

batch_size = 500
found = []

for offset in range(0, total, batch_size):

    data = collection.get(
        offset=offset,
        limit=batch_size,
        include=["documents", "metadatas"],
    )

    documents = data.get("documents") or []
    metadatas = data.get("metadatas") or []

    for document, metadata in zip(documents, metadatas):

        if target.lower() in document.lower():

            found.append(
                {
                    "content": document,
                    "metadata": metadata,
                }
            )

    if offset % 5000 == 0:
        print(f"Checked {offset}/{total} chunks...")

print()
print("=" * 80)
print("RESULT")
print("=" * 80)

print("Luna matches:", len(found))

for i, item in enumerate(found, start=1):

    print()
    print(f"MATCH {i}")
    print("-" * 80)
    print("Metadata:")
    print(item["metadata"])
    print()
    print("Content:")
    print(item["content"])
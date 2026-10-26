import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
from app.ingestion.embed_store import get_vectorstore


vectorstore = get_vectorstore()
collection = vectorstore._collection

queries = [
    "Luna-371",
    "What is the temperament of Luna-371?",
    "What is the breed of Luna-371?",
    "PET-000371",
]

target_text = "Luna-371"

print("=" * 80)
print("EMBEDDING RANK TEST")
print("=" * 80)

# ---------------------------------------------------------
# Find target document + stored embedding
# ---------------------------------------------------------

total = collection.count()

batch_size = 500

target_embedding = None
target_document = None

print(f"Total chunks: {total}")

for offset in range(0, total, batch_size):

    data = collection.get(
        offset=offset,
        limit=batch_size,
        include=["documents", "metadatas", "embeddings"],
    )

    documents = data.get("documents") or []
    metadatas = data.get("metadatas") or []
    embeddings = data.get("embeddings")

    if embeddings is None:
        embeddings = []

    for document, metadata, embedding in zip(
        documents,
        metadatas,
        embeddings,
    ):

        if target_text.lower() in document.lower():

            target_document = document
            target_embedding = np.array(embedding)

            print("\nFOUND TARGET DOCUMENT")
            print("Metadata:", metadata)
            print("Embedding dimension:", len(target_embedding))

            break

    if target_embedding is not None:
        break


if target_embedding is None:
    print("ERROR: Target document not found.")
    sys.exit(1)


# ---------------------------------------------------------
# Test each query
# ---------------------------------------------------------

for query in queries:

    print("\n")
    print("=" * 80)
    print("QUERY:", query)
    print("=" * 80)

    query_embedding = np.array(
        vectorstore._embedding_function.embed_query(query)
    )

    target_distance = np.linalg.norm(
        query_embedding - target_embedding
    )

    print("Target distance:", target_distance)

    # -----------------------------------------------------
    # Calculate distances against ALL Chroma embeddings
    # -----------------------------------------------------

    closer_count = 0

    nearest = []

    for offset in range(0, total, batch_size):

        data = collection.get(
            offset=offset,
            limit=batch_size,
            include=["documents", "metadatas", "embeddings"],
        )

        documents = data.get("documents") or []
        metadatas = data.get("metadatas") or []
        embeddings = data.get("embeddings")

        if embeddings is None:
            continue

        embeddings = np.asarray(embeddings)

        # Vectorized L2 distance
        distances = np.linalg.norm(
            embeddings - query_embedding,
            axis=1,
        )

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        ):

            if distance < target_distance:
                closer_count += 1

            nearest.append(
                (
                    float(distance),
                    document,
                    metadata,
                )
            )

    rank = closer_count + 1

    print()
    print("TARGET RANK:", rank)
    print("Documents closer than target:", closer_count)

    # -----------------------------------------------------
    # Show nearest documents
    # -----------------------------------------------------

    nearest.sort(key=lambda x: x[0])

    print()
    print("TOP 10 NEAREST DOCUMENTS:")
    print("-" * 80)

    for i, (distance, document, metadata) in enumerate(
        nearest[:10],
        start=1,
    ):

        print()
        print(f"{i}. Distance: {distance:.4f}")
        print("Source:", metadata.get("source"))
        print("Page:", metadata.get("page_label"))

        print(
            document[:300]
            .replace("\n", " ")
        )

    # -----------------------------------------------------
    # Find target in sorted results
    # -----------------------------------------------------

    for i, (distance, document, metadata) in enumerate(
        nearest,
        start=1,
    ):

        if target_text.lower() in document.lower():

            print()
            print("TARGET FOUND IN SORTED RESULTS")
            print("Actual rank:", i)
            print("Distance:", distance)
            break 
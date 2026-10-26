import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.embed_store import get_vectorstore


vectorstore = get_vectorstore()
collection = vectorstore._collection

target = "Luna-371"

print("=" * 80)
print("DIRECT EMBEDDING TEST")
print("=" * 80)

# ---------------------------------------------------------
# 1. Find Luna-371 in Chroma
# ---------------------------------------------------------

total = collection.count()

batch_size = 500
target_document = None
target_metadata = None

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

        if target.lower() in document.lower():

            target_document = document
            target_metadata = metadata
            target_embedding = embedding

            print("\nFOUND TARGET")
            print("Metadata:")
            print(target_metadata)

            print("\nDocument:")
            print(target_document)

            print("\nEmbedding dimension:")
            print(len(target_embedding))

            break

    if target_document:
        break


if not target_document:
    print("Luna-371 not found.")
    sys.exit(1)


# ---------------------------------------------------------
# 2. Generate embedding for query
# ---------------------------------------------------------

print("\n" + "=" * 80)
print("GENERATING QUERY EMBEDDING")
print("=" * 80)

query = "Luna-371"

query_embedding = vectorstore._embedding_function.embed_query(query)

print("Query:", query)
print("Query embedding dimension:", len(query_embedding))


# ---------------------------------------------------------
# 3. Calculate L2 distance
# ---------------------------------------------------------

import numpy as np

target_vector = np.array(target_embedding)
query_vector = np.array(query_embedding)

distance = np.linalg.norm(
    target_vector - query_vector
)

print("\n" + "=" * 80)
print("DISTANCE")
print("=" * 80)

print("L2 distance:", distance)
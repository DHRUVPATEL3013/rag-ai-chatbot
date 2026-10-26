

from app.ingestion.embed_store import get_vectorstore


query = "Hi"

vectorstore = get_vectorstore()

results = vectorstore.similarity_search(
    query,
    k=20,
)

print("=" * 60)
print("TOP 20 RESULTS")
print("=" * 60)

for i, document in enumerate(results, start=1):
    source = document.metadata.get("source", "")
    page = document.metadata.get("page")

    print(f"{i}. Page: {page} | Source: {source}")
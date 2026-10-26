from app.ingestion.embed_store import get_vectorstore


query_words = [
    "visitor",
    "reception",
    "registered",
]

vectorstore = get_vectorstore()

result = vectorstore._collection.get(
    include=["documents", "metadatas"]
)

print("=" * 60)
print("KEYWORD SEARCH")
print("=" * 60)

for i, document in enumerate(result["documents"]):
    text = document.lower()

    if all(word in text for word in query_words):
        metadata = result["metadatas"][i]

        print("MATCH FOUND")
        print("Source:", metadata.get("source"))
        print()
        print(document)
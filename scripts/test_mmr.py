from app.ingestion.embed_store import get_vectorstore


queries = [
    "visitor access",
    "visitors reception",
    "visitor registration",
    "employees responsible for approved visitors",
]

vectorstore = get_vectorstore()

for query in queries:
    print("\n" + "=" * 60)
    print(f"QUERY: {query}")
    print("=" * 60)

    results = vectorstore.similarity_search_with_score(
        query,
        k=5,
    )

    for i, (document, score) in enumerate(results, start=1):
        source = document.metadata.get("source", "")
        page = document.metadata.get("page")

        print(
            f"{i}. Score: {score:.3f} | "
            f"Page: {page} | "
            f"Source: {source}"
        )
# from app.ingestion.embed_store import get_vectorstore
# from app.retrieval.confidence import is_low_confidence


# vectorstore = get_vectorstore()

# query = "Tell me about employee leave."

# results = vectorstore.similarity_search_with_score(
#     query,
#     k=3,
# )

# print(f"Number of results: {len(results)}")

# for index, (document, score) in enumerate(results, start=1):
#     print(f"\n--- Result {index} ---")
#     print("Score:", score)
#     print("Content:")
#     print(document.page_content)

# print("\nLow confidence:", is_low_confidence(results))


from app.ingestion.embed_store import get_vectorstore
from app.retrieval.confidence import is_low_confidence

vectorstore = get_vectorstore()

queries = [
    "How many days of annual leave do employees get?",
    "Tell me about employee leave.",
    "How many days of medical leave do employees get?",
    "How much can employees claim for meals during business travel?",
    "How many days can employees work remotely?",
    "What is the company's office address?",
    "What is the CEO's name?",
    "What is the company's revenue?",
]

for query in queries:
    print(f"\n{'=' * 60}")
    print(f"Query: {query}")

    results = vectorstore.similarity_search_with_score(
        query,
        k=1,
    )

    if not results:
        print("No results found.")
        continue

    document, score = results[0]

    print(f"Score: {score}")
    print("Retrieved content:")
    print(document.page_content)


results = vectorstore.similarity_search_with_score(query, k=1)

print("=" * 60)
print(f"Query: {query}")

for document, score in results:
    print(f"Score: {score}")
    print(f"Retrieved content:\n{document.page_content}")

print(
    "Low confidence:",
    is_low_confidence(results),
)
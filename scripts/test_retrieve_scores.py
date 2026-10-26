# from app.retrieval.retriever import retrieve_with_scores


# # queries = [
# #     "How many days of annual leave do employees get?",
# #     "What is the company's office address?",
# # ]

# # queries = ["health insurance after completing probation",
# #            "How many days of annual leave do employees get?",
# #            "What is the company's office address?",
# #            "What is the CEO's name?",
# #            "How many hours should employees work per day?",
# #            "How much is the transport allowance?",
# #            "How much can employees claim for learning?",
# #            "How many days can employees work remotely?"]

# queries = ["Visitors must be registered at reception before entering the office"]


# for query in queries:
#     print("\n" + "=" * 60)
#     print(f"Query: {query}")

#     results = retrieve_with_scores(query, k=10)

#     for index, (document, score) in enumerate(results, start=1):
#         print(f"\nResult {index}")
#         print(f"Score: {score}")
#         print(f"Source: {document.metadata.get('source')}")
#         print(f"Content:\n{document.page_content}")


from app.ingestion.embed_store import get_vectorstore


query = "What is required for visitor access?"

vectorstore = get_vectorstore()

results = vectorstore.similarity_search_with_score(
    query,
    k=148,
)

print("=" * 60)
print("ALL RESULTS")
print("=" * 60)

for i, (document, score) in enumerate(results, start=1):
    source = document.metadata.get("source", "")
    page = document.metadata.get("page")

    print(f"{i}. Score: {score:.3f} | Page: {page} | Source: {source}")
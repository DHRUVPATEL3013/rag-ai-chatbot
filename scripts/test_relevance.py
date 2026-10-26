from app.retrieval.retriever import retrieve_with_scores
from app.retrieval.confidence import filter_relevant_documents


query = ["What time does the cafeteria close?"]


results = retrieve_with_scores(query, k=10)

print("\nRetrieved documents:")

for document, score in results:
    print(f"\nScore: {score}")
    print(f"Source: {document.metadata.get('source')}")


filtered_results = filter_relevant_documents(results)

print("\n" + "=" * 60)
print("After relevance filtering:")

for document, score in filtered_results:
    print(f"\nScore: {score}")
    print(f"Source: {document.metadata.get('source')}")
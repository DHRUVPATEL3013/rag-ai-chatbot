from app.retrieval.retriever import retrieve_with_scores

results = retrieve_with_scores(
    # "What is the salary of EMP-000001?",
    "What is the salary of  EMP-040054 ?",
    k=10,
)

for i, (doc, score) in enumerate(results, 1):
    print("=" * 60)
    print(f"RESULT {i} | SCORE: {score}")
    print(doc.page_content)
    print(doc.metadata)
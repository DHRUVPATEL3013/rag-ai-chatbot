from app.retrieval.hybrid import hybrid_search


QUESTIONS = [
    "How many annual leave days does a full-time employee receive each year?",
    "How many unused annual leave days can be carried into the next year?",
    "How many weeks of parental leave are available to eligible employees?",
    "What is the standard notice period for confirmed employees?",
]


for query in QUESTIONS:
    print("\n" + "=" * 100)
    print("QUESTION:", query)
    print("=" * 100)

    results = hybrid_search(query, k=10)

    for rank, result in enumerate(results, start=1):
        metadata = result["document"].metadata

        print(
            f"Rank {rank:2} | "
            f"Combined: {result['combined_score']:.6f} | "
            f"Semantic: {result['semantic_rank']} | "
            f"Keyword: {result['keyword_rank']} | "
            f"File: {metadata.get('filename')}"
        )
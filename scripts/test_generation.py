# from app.generation.generator import generate_answer
# from app.retrieval.retriever import get_retriever


# retriever = get_retriever(k=2)


# queries = [
#     "How many days of annual leave do employees get?",
#     "How many hours should employees work per day?",
#     "What is the company's office address?",
# ]


# for query in queries:
#     print("\n" + "=" * 60)
#     print(f"Question: {query}")

#     documents = retriever.invoke(query)

#     answer = generate_answer(
#         query=query,
#         documents=documents,
#     )

#     print("\nAnswer:")
#     print(answer)


from app.generation.generator import generate_answer
# from app.retrieval.embed_store import get_vectorstore
from app.ingestion.embed_store import get_vectorstore


vectorstore = get_vectorstore()


queries = [
    "How many days of annual leave do employees get?",
    "How many hours should employees work per day?",
    "What is the company's office address?",
]


for query in queries:
    print("\n" + "=" * 60)
    print(f"Question: {query}")

    results = vectorstore.similarity_search_with_score(
        query,
        k=2,
    )

    answer = generate_answer(
        query=query,
        retrieved_docs_with_scores=results,
    )

    print("\nAnswer:")
    print(answer)
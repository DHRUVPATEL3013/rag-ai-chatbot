
# from app.retrieval.retriever import get_retriever


# retriever = get_retriever(k=3)

# query = "How many days of annual leave do employees get?"

# documents = retriever.invoke(query)

# print(f"Number of results: {len(documents)}")

# for index, document in enumerate(documents, start=1):
#     print(f"\n--- Result {index} ---")
#     print(document.page_content)
#     print("\nMetadata:")
#     print(document.metadata)



# -----------------------------




from app.retrieval.retriever import get_retriever


retriever = get_retriever(k=10)

queries = [
    "How much is the transport allowance?",
    # "How many days of annual leave do employees get?",
    # "How many hours should employees work per day?",
    # "How much can employees claim for meals during business travel?",
    # "How many days can employees work remotely?",
    # "What is the company's office address?",
    # "How many days of medical leave are employees entitled to?",
    # "How much can employees claim for meals during business travel?",
    # "How many days can employees work remotely?",
    # "What is the company's office address?",
    # "What is the CEO's name?",
    # "What is the company's revenue?"
]


for query in queries:
    print("\n" + "=" * 60)
    print(f"Query: {query}")

    results = retriever.invoke(query)

    print(f"Number of results: {len(results)}")

    for index, document in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(document.page_content)
        print("\nSource:")
        print(document.metadata.get("source"))
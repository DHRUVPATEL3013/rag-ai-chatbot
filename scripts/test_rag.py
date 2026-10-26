from app.generation.generator import generate_rag_answer


# queries = [
#     "How many days of annual leave do employees get?",
#     "How many hours should employees work per day?",
#     "How much is the transport allowance?",
#     "How much can employees claim for learning?",
#     "How many days can employees work remotely?",
#     "What is the company's office address?",
#     "What is the CEO's name?",
# ]

queries = [
    # "What time does the cafeteria open?",
    # "What time does the cafeteria close?",
    # "What is required for parking access?",
    # "How should meeting rooms be reserved?",
    "What is required for visitor access?",
    # "what is the company's office address?",
    # "What is the CEO's name?",
    ]


for query in queries:
    print("\n" + "=" * 60)
    print(f"Question: {query}")

    result = generate_rag_answer(query)

    print("\nAnswer:")
    print(result["answer"])

    print("\nSources:")
    for source in result["sources"]:
        print(source)
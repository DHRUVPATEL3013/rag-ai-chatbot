

from app.generation.query_rewriter import rewrite_query


history = [
    {
        "role": "user",
        "content": "How many days of medical leave?",
    },
    {
        "role": "assistant",
        "content": "12 days per year.",
    },
    {
        "role": "user",
        "content": "What about casual leave?",
    },
    {
        "role": "assistant",
        "content": "7 days per year.",
    },
    {
        "role": "user",
        "content": "and what about annual leaves?",
    },
    {
        "role": "assistant",
        "content": "21 days per year.",
    },
]


queries = [
    "and annual?",
    "what is the combined leave of these three?",
    "what about the previous one?",
    "how many days of annual leave?",
]


for query in queries:

    print("=" * 60)
    print("USER:", query)

    rewritten = rewrite_query(
        query=query,
        conversation_history=history,
    )

    print("REWRITTEN:", rewritten)
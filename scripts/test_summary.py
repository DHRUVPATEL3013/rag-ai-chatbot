from app.memory.summary import summarize_conversation


messages = [
    {
        "role": "user",
        "content": "How many days of medical leave?",
    },
    {
        "role": "assistant",
        "content": "Employees are entitled to 12 days of medical leave per year.",
    },
    {
        "role": "user",
        "content": "What about casual leave?",
    },
    {
        "role": "assistant",
        "content": "Employees are entitled to 7 days of casual leave per year.",
    },
    {
        "role": "user",
        "content": "and annual?",
    },
    {
        "role": "assistant",
        "content": "Employees are entitled to 21 days of annual leave per year.",
    },
]


summary = summarize_conversation(messages)

print("=" * 60)
print("CONVERSATION SUMMARY")
print("=" * 60)
print(summary)
print("=" * 60)
"""
Conversation-aware query contextualization.

Converts follow-up questions into standalone retrieval queries.
"""

from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq

# from app.config import settings
from app.llm import get_llm


# def get_query_rewriter():
#     """
#     Create the LLM used for query contextualization.
#     """

#     return ChatGroq(
#         model=settings.GROQ_MODEL,
#         api_key=settings.GROQ_API_KEY,
#         temperature=0,
#     )


def rewrite_query(
    query: str,
    conversation_history: list | None = None,
) -> str:
    """
    Convert a context-dependent user question into a
    standalone search query.

    If there is no conversation history, return the original query.
    """

    if not conversation_history:
        return query

    history = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in conversation_history
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a search-query contextualizer for an internal
company knowledge-base chatbot.

Your job is NOT to answer the user's question.

Rewrite the user's latest question into a standalone
search query that contains all information necessary
for retrieving the correct internal documents.

Rules:

1. Use the conversation history to resolve references such as:
   "it", "that", "this", "these", "those", "the previous one",
   "the above", "these three", etc.

2. Preserve the user's actual intent.

3. Do not invent information.

4. Do not answer the question.

5. If the user's question is already standalone,
   return it unchanged or make only a minimal cleanup.

6. Return ONLY the rewritten search query.
""",
            ),
            (
                "human",
                """
Conversation history:

{history}

Latest user question:

{question}

Standalone search query:
""",
            ),
        ]
    )

    # chain = prompt | get_query_rewriter()
    chain = prompt | get_llm()

    response = chain.invoke(
        {
            "history": history,
            "question": query,
        }
    )

    return response.content.strip()
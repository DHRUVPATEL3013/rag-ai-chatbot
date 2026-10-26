"""
Build a standalone retrieval query using the current question,
conversation summary, and recent conversation context.
"""

from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq

# from app.config import settings
from app.llm import get_llm


# def get_query_rewriter_llm():
#     return ChatGroq(
#         model=settings.GROQ_MODEL,
#         api_key=settings.GROQ_API_KEY,
#         temperature=0,
#     )


def build_retrieval_query(
    query: str,
    conversation_history: list | None = None,
    conversation_summary: str | None = None,
) -> str:
    """
    Convert a contextual user question into a standalone
    retrieval query.

    Uses:
    - conversation summary for older context
    - latest messages for recent context
    - current question
    """

    if not conversation_history and not conversation_summary:
        return query

    recent_messages = (conversation_history or [])[-10:]

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_messages
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You rewrite user questions into standalone search queries.

The query will be used to search an internal company knowledge base.

Rules:
1. Resolve references such as:
   - "it"
   - "that"
   - "this"
   - "previous one"
   - "these three"
   - "and annual?"
2. Use the conversation summary and recent conversation when needed.
3. Preserve the user's actual intent.
4. Do not answer the question.
5. Do not invent information.
6. Return ONLY the standalone search query.
7. Make the query explicit enough for semantic search.
""",
            ),
            (
                "human",
                """Conversation summary:
{summary}

Recent conversation:
{history}

Current user question:
{question}

Standalone search query:""",
            ),
        ]
    )

    # chain = prompt | get_query_rewriter_llm()
    chain = prompt | get_llm()

    response = chain.invoke(
        {
            "summary": conversation_summary or "(No summary available)",
            "history": history_text or "(No recent conversation)",
            "question": query,
        }
    )

    rewritten_query = response.content.strip()

    return rewritten_query or query
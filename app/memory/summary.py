"""
Conversation memory summarization.

Creates a compact summary of older chat messages so the
query rewriter can understand long conversations without
sending the entire history to the LLM.
"""

from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq

# from app.config import settings
from app.llm import get_llm

# def get_summary_llm():
#     return ChatGroq(
#         model=settings.GROQ_MODEL,
#         api_key=settings.GROQ_API_KEY,
#         temperature=0,
#     )


def summarize_conversation(
    messages: list,
    existing_summary: str | None = None,
) -> str:
    """
    Create or update a conversation summary.

    The summary should preserve:
    - important facts
    - user preferences
    - topics discussed
    - references needed to understand future questions

    It should remove:
    - greetings
    - unnecessary wording
    - repetitive conversation
    """

    if not messages:
        return existing_summary or ""

    conversation_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in messages
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You maintain memory for a company internal knowledge-base chatbot.

Create a concise conversation summary that helps the chatbot
understand future follow-up questions.

Preserve:
1. Important facts discussed.
2. Policies or values mentioned.
3. The user's intent and topics.
4. References such as "these three", "previous one", etc.
   when their meaning can be determined from the conversation.
5. Important context needed for future questions.

Do NOT:
1. Invent facts.
2. Answer unanswered questions.
3. Add information from your general knowledge.
4. Include greetings or unnecessary conversational text.

If an existing summary is provided, update it using the
new conversation messages.

Return ONLY the updated summary.
""",
            ),
            (
                "human",
                """Existing summary:
{existing_summary}

New conversation messages:
{conversation}

Updated conversation summary:""",
            ),
        ]
    )

    # chain = prompt | get_summary_llm()
    chain = prompt | get_llm()

    response = chain.invoke(
        {
            "existing_summary": existing_summary or "(No existing summary)",
            "conversation": conversation_text,
        }
    )

    return response.content.strip()
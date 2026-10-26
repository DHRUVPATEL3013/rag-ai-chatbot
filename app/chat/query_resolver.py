"""
Conversation-aware query resolver.

Resolves follow-up questions using:
- recent conversation history
- conversation summary
- dynamically extracted entities
"""

import re

from langchain_core.prompts import ChatPromptTemplate
# from langchain_groq import ChatGroq

# from app.config import settings
from app.llm import get_llm

# ---------------------------------------------------------
# LLM
# ---------------------------------------------------------

# def get_llm():
#     return ChatGroq(
#         model=settings.GROQ_MODEL,
#         api_key=settings.GROQ_API_KEY,
#         temperature=0,
#     )


# ---------------------------------------------------------
# Entity extraction
# ---------------------------------------------------------

def extract_context_entities(
    conversation_history: list | None = None,
    conversation_summary: str | None = None,
) -> dict:
    """
    Extract useful entities from the conversation.

    Currently detects employee IDs dynamically.
    More entity types can be added later without changing
    the resolver logic.
    """

    text_parts = []

    if conversation_summary:
        text_parts.append(conversation_summary)

    if conversation_history:
        for message in conversation_history:
            text_parts.append(
                message.get("content", "")
            )

    text = "\n".join(text_parts)

    # Employee IDs such as:
    # EMP-000001
    # EMP-040054
    employee_ids = re.findall(
        r"\bEMP-\d{6}\b",
        text,
        flags=re.IGNORECASE,
    )

    # Preserve order while removing duplicates.
    employee_ids = list(
        dict.fromkeys(
            employee.upper()
            for employee in employee_ids
        )
    )

    return {
        "employee_ids": employee_ids,
    }


# ---------------------------------------------------------
# Context formatting
# ---------------------------------------------------------

def build_entity_context(
    conversation_history: list | None = None,
    conversation_summary: str | None = None,
) -> str:

    entities = extract_context_entities(
        conversation_history=conversation_history,
        conversation_summary=conversation_summary,
    )

    lines = []

    if entities["employee_ids"]:
        lines.append(
            "Recently mentioned employee IDs: "
            + ", ".join(entities["employee_ids"])
        )

        # Most recently mentioned employee
        lines.append(
            "Most recently mentioned employee: "
            + entities["employee_ids"][-1]
        )

        # Previous employee
        if len(entities["employee_ids"]) >= 2:
            lines.append(
                "Previous relevant employee: "
                + entities["employee_ids"][-2]
            )

    if not lines:
        return "No structured entities detected."

    return "\n".join(lines)


# ---------------------------------------------------------
# Query resolver
# ---------------------------------------------------------

def resolve_query(
    query: str,
    conversation_history: list | None = None,
    conversation_summary: str | None = None,
) -> str:
    """
    Resolve the user's current question into a
    self-contained question.

    The resolver dynamically uses conversation context
    instead of hardcoding specific employee IDs.
    """

    if not conversation_history and not conversation_summary:
        return query

    history_text = "No previous conversation."

    if conversation_history:
        history_text = "\n".join(
            f"{message['role'].upper()}: "
            f"{message['content']}"
            for message in conversation_history
        )

    summary_text = (
        conversation_summary
        if conversation_summary
        else "No conversation summary."
    )

    entity_context = build_entity_context(
        conversation_history=conversation_history,
        conversation_summary=conversation_summary,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are a conversation-aware query resolver.

Your job is to rewrite the user's CURRENT question into a
self-contained question using the conversation context.

You MUST NOT answer the question.

You MUST preserve the user's intent.

---------------------------------------------------------
REFERENCE RESOLUTION
---------------------------------------------------------

Resolve references dynamically using the most relevant
entities from the conversation.

Examples:

"this employee"
→ the most recently relevant employee

"that employee"
→ the relevant employee from the previous context

"their salary"
→ salary of the currently referenced employee

"both"
→ the two most recently relevant entities when the
conversation clearly contains two comparable entities

"these employees"
→ the currently referenced employee set

"previous employee"
→ the previous relevant employee

"those two"
→ the two most recently relevant matching entities

---------------------------------------------------------
IMPORTANT
---------------------------------------------------------

Do NOT assume that "both" always means employees.

Determine what "both", "these", "those", "their", etc.
refer to from the conversation.

For example:

User:
What is the salary of EMP-000001?

User:
What is the salary of EMP-040054?

User:
What is the total of both?

Resolved:
What is the total salary of EMP-000001 and EMP-040054?

Another example:

User:
Which department is EMP-000001 in?

User:
What about EMP-000002?

User:
Are both in the same department?

Resolved:
Are EMP-000001 and EMP-000002 in the same department?

---------------------------------------------------------
RULES
---------------------------------------------------------

1. Preserve the original intent.

2. Resolve references using recent conversation first.

3. Use the conversation summary when older context
   is required.

4. Prefer the most recent relevant entities.

5. Do not invent entities, values, or facts.

6. Do not answer the question.

7. If the question is already self-contained,
   return it unchanged.

8. Return ONLY the resolved question.

---------------------------------------------------------
STRUCTURED CONTEXT
---------------------------------------------------------

{entity_context}

---------------------------------------------------------
CONVERSATION SUMMARY
---------------------------------------------------------

{summary}

---------------------------------------------------------
RECENT CONVERSATION
---------------------------------------------------------

{history}
""",
            ),
            (
                "human",
                """
Current question:

{question}

Resolved question:
""",
            ),
        ]
    )

    chain = prompt | get_llm()

    response = chain.invoke(
        {
            "entity_context": entity_context,
            "summary": summary_text,
            "history": history_text,
            "question": query,
        }
    )

    resolved_query = response.content.strip()

    print("=" * 60)
    print("[QUERY RESOLVER]")
    print("Original :", query)
    print("Entities :", entity_context)
    print("Resolved :", resolved_query)
    print("=" * 60)

    return resolved_query
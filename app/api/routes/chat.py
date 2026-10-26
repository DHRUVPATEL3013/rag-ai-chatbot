"""
Chat API endpoints.

Handles:
- Chat sessions
- Chat history
- RAG question answering
- Saving user/assistant messages
"""
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from app.chat.static_responses import get_static_greeting

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Query

from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ChatMessage,
    ChatSession,
    PopularQuery,
)
from app.db.session import get_db
from app.generation.generator import generate_rag_answer
from app.ingestion.language_detect import detect_language
from app.security.pii import validate_question

from app.memory.manager import (
    should_update_summary,
    create_or_update_summary,
)
from app.chat.query_router import classify_query
# from app.chat.duckdb_query import query_duckdb
from app.chat.duckdb_query import query_duckdb, execute_structured_query
from app.chat.query_intent import detect_simple_intent

from app.chat.query_resolver import resolve_query
from app.retrieval.ambiguity import is_ambiguous_query

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: str | None = None
    question: str
    k: int = 10


# ---------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------

@router.post("")
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Ask a question and maintain conversation history.
    """

    # # -----------------------------------------------------
    # # 0. Validate user question
    # # -----------------------------------------------------

    is_valid, validation_message = validate_question(
        request.question
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=validation_message,
        )

    is_ambiguous = is_ambiguous_query(request.question)

    if is_ambiguous:
            return {
                        "answer": (
                            "Could you clarify what you would like to know? "
                            "For example, you can ask about the number of "
                            "annual leave days, eligibility, or the leave "
                            "application process."
                        ),
                        "sources": [],
                        "source": "Clarification",
                    }

    

    # -----------------------------------------------------
    # 1. Get or create session
    # -----------------------------------------------------

    session_id = request.session_id

    if not session_id:
        session_id = str(uuid4())

    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.session_id == session_id)
    )

    chat_session = result.scalar_one_or_none()

    if chat_session is None:
        chat_session = ChatSession(
            session_id=session_id,
            user_id=None,
            expires_at=None,
        )

        db.add(chat_session)

        await db.flush()

    # -----------------------------------------------------
    # 2. Load previous conversation
    # -----------------------------------------------------

    history_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == chat_session.id
        )
        .order_by(ChatMessage.created_at.asc())
    )

    history_messages = history_result.scalars().all()

    previous_message = (
        history_messages[-1]
        if history_messages
        else None
    )

    # Keep only the latest 10 messages.
    history_messages = history_messages[-10:]

    conversation_summary = chat_session.conversation_summary

    conversation_history = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in history_messages
    ]

    print("\n" + "=" * 60)
    print("SESSION:", session_id)
    print("SUMMARY:", conversation_summary)
    print("HISTORY:")
    for message in conversation_history:
        print(f"{message['role'].upper()}: {message['content']}")
    print("=" * 60)

    # -----------------------------------------------------
    # 3. Save current user message
    # -----------------------------------------------------

    user_message = ChatMessage(
        session_id=chat_session.id,
        user_id=None,
        role="user",
        content=request.question,
        language=None,
        source="user",
        previous_message_id=(
            previous_message.id
            if previous_message
            else None
        ),
    )
    

    db.add(user_message)

    await db.flush()


    # -----------------------------------------------------
    # Track popular query
    # -----------------------------------------------------

    await track_popular_query(
        db=db,
        question=request.question,
    )

    # -----------------------------------------------------
    # 4. Check static response
    # -----------------------------------------------------

    greeting = get_static_greeting(request.question)

    if greeting:
        result = {
            "answer": greeting,
            "sources": [],
            "source": "Static Response",
        }

    else:
    #     # -------------------------------------------------
    #     # 5. RAG + LLM
    #     # -------------------------------------------------

    #     result = generate_rag_answer(
    #         query=request.question,
    #         k=request.k,
    #         conversation_history=conversation_history,
    #         conversation_summary=conversation_summary,
    #     )

        # -------------------------------------------------
        # 5. Route query: DuckDB or RAG
        # -------------------------------------------------

        # resolved_query = resolve_query(
        #     query=request.question,
        #     conversation_history=conversation_history,
        #     conversation_summary=conversation_summary,
        # )

        # route = classify_query(resolved_query)

        # Route first using the original question.
        route = classify_query(request.question)

        resolved_query = request.question

        # Only resolve context for RAG.
        if route == "rag":
            resolved_query = resolve_query(
                query=request.question,
                conversation_history=conversation_history,
                conversation_summary=conversation_summary,
            )
        
        print("=" * 60)
        print(f"[ROUTER] Original query : {request.question}")
        print(f"[ROUTER] Resolved query : {resolved_query}")
        print(f"[ROUTER] Selected route : {route}")
        print("=" * 60)

        if route == "duckdb":

            answer = query_duckdb(resolved_query)
            print("answer--------",answer)

            if answer:
                result = {
                    "answer": answer,
                    "sources": ["Excel / DuckDB"],
                    "source": "DuckDB",
                }
            else:
                result = {
                    "answer": (
                        "I couldn't find enough information in the Excel "
                        "data to answer that question."
                    ),
                    "sources": ["Excel / DuckDB"],
                    "source": "DuckDB",
                }

            if answer:
                result = {
                    "answer": answer,
                    "sources": ["Excel / DuckDB"],
                    "source": "DuckDB",
                }
            else:
                # Safety fallback to existing RAG
                result = generate_rag_answer(
                    query=request.question,
                    k=request.k,
                    conversation_history=conversation_history,
                    conversation_summary=conversation_summary,
                )

        else:
            # -------------------------------------------------
            # Existing RAG
            # -------------------------------------------------

            result = generate_rag_answer(
                query=request.question,
                k=request.k,
                conversation_history=conversation_history,
                conversation_summary=conversation_summary,
            )

    # -----------------------------------------------------
    # 6. Save assistant response
    # -----------------------------------------------------

    assistant_message = ChatMessage(
        session_id=chat_session.id,
        user_id=None,
        role="assistant",
        content=result.get("answer", ""),
        language=result.get("language"),
        source=result.get(
            "source",
            "Internal Knowledge",
        ),
        citations=result.get("sources", []),
        previous_message_id=user_message.id,
    )

    db.add(assistant_message)

    await db.flush()

    # ---------------------------------------------------------
    # 7. Update conversation summary when required
    # ---------------------------------------------------------

    message_count_result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == chat_session.id
        )
        .order_by(ChatMessage.created_at.asc())
    )

    all_messages = message_count_result.scalars().all()

    message_count = len(all_messages)
    message_count = 0

    print(f"[SUMMARY] Message count: {message_count}")
    print(f"[SUMMARY] Should update: {should_update_summary(message_count)}")

    if should_update_summary(message_count):

        print("[SUMMARY] Starting LLM summary generation...")

        summary_messages = [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in all_messages
        ]

        chat_session.conversation_summary = (
            create_or_update_summary(
                messages=summary_messages,
                existing_summary=chat_session.conversation_summary,
            )
        )

        print("[SUMMARY] Summary generation completed.")

    # Update session timestamp.
    chat_session.updated_at = datetime.now(timezone.utc)

    await db.commit()

    # -----------------------------------------------------
    # 7. Return response
    # -----------------------------------------------------

    return {
        "session_id": session_id,
        "message_id": assistant_message.id,
        "answer": result.get("answer", ""),
        "source": result.get(
            "source",
            "Internal Knowledge",
        ),
        "sources": result.get("sources", []),
    }





@router.get("/history")
async def get_chat_history(
    db: AsyncSession = Depends(get_db),
):
    """
    Return recent chat sessions.
    """

    result = await db.execute(
        select(ChatSession)
        .order_by(ChatSession.updated_at.desc())
    )

    sessions = result.scalars().all()

    history = []

    for session in sessions:

        message_result = await db.execute(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session.id
            )
            .order_by(
                ChatMessage.created_at.asc()
            )
        )

        messages = message_result.scalars().all()

        if not messages:
            continue

        # Use the first user question as the title.
        first_user_message = next(
            (
                message
                for message in messages
                if message.role == "user"
            ),
            None,
        )

        title = (
            first_user_message.content
            if first_user_message
            else "New conversation"
        )

        # Keep the title short.
        if len(title) > 60:
            title = title[:60] + "..."

        history.append(
            {
                "session_id": session.session_id,
                "title": title,
                "updated_at": session.updated_at,
                "message_count": len(messages),
            }
        )

    return {
        "items": history,
        "total": len(history),
    }


@router.get("/history/{session_id}")
async def get_chat_history_messages(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Return all messages for one conversation.
    """

    result = await db.execute(
        select(ChatSession).where(
            ChatSession.session_id == session_id
        )
    )

    chat_session = result.scalar_one_or_none()

    if chat_session is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.session_id == chat_session.id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
    )

    messages = result.scalars().all()

    return {
        "session_id": session_id,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "source": message.source,
                "citations": message.citations,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }

#ppppppppppppppppppppppppppppppppppp#

def should_track_query(question: str) -> bool:
    """
    Decide whether the question should be stored
    in popular_queries.

    Ignore simple conversational messages.
    """

    question = question.strip()

    if len(question) < 5:
        return False

    ignored_queries = {
        "hi",
        "hello",
        "hey",
        "okay",
        "ok",
        "thanks",
        "thank you",
        "perfect",
        "nice",
        "nice work",
        "good",
        "great",
        "bye",
    }

    if question.lower() in ignored_queries:
        return False

    return True



async def track_popular_query(
    db: AsyncSession,
    question: str,
):
    """
    Insert a new popular query or increment
    the hit_count of an existing query.
    """

    question = question.strip()

    if not should_track_query(question):
        return

    try:
        language = detect_language(question)
    except Exception:
        language = None

    result = await db.execute(
        select(PopularQuery).where(
            PopularQuery.query_text == question,
            PopularQuery.language == language,
        )
    )

    popular_query = result.scalar_one_or_none()

    if popular_query is not None:

        popular_query.hit_count += 1
        popular_query.updated_at = datetime.now(
            timezone.utc
        )

    else:

        popular_query = PopularQuery(
            query_text=question,
            language=language,
            hit_count=1,
        )

        db.add(popular_query)

    
# ---------------------------------------------------------
# GET /chat/suggestions
# ---------------------------------------------------------

@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(
        ...,
        min_length=2,
        description="Text to search for in popular queries.",
    ),
    limit: int = Query(
        5,
        ge=1,
        le=20,
        description="Maximum number of suggestions.",
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Return popular queries matching the user's input.
    """

    search_text = q.strip()

    if not search_text:
        return {
            "suggestions": []
        }

    # Same input restrictions used by /chat
    if len(search_text) > 10000:
        return {
            "suggestions": []
        }

    if len(search_text.split()) > 1000:
        return {
            "suggestions": []
        }

    result = await db.execute(
        select(PopularQuery)
        .where(
            func.lower(
                PopularQuery.query_text
            ).contains(
                search_text.lower()
            )
        )
        .order_by(
            PopularQuery.hit_count.desc(),
            PopularQuery.updated_at.desc(),
        )
        .limit(limit)
    )

    queries = result.scalars().all()

    return {
        "suggestions": [
            {
                "query": item.query_text,
                "language": item.language,
                "hit_count": item.hit_count,
            }
            for item in queries
        ]
    }
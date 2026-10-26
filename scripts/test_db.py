"""
Test PostgreSQL chat-history functionality.

Tests:
1. Database connection
2. Create a chat session
3. Save user message
4. Save assistant message
5. Read conversation history
6. Clean up test data
"""

import asyncio
from datetime import datetime, timezone

from sqlalchemy import select

from app.db.models import ChatMessage, ChatSession
from app.db.session import AsyncSessionLocal


async def test_db():
    async with AsyncSessionLocal() as db:

        # ---------------------------------------------------------
        # 1. Create a test session
        # ---------------------------------------------------------

        session = ChatSession(
            session_id="test-session-123",
            user_id="test-user",
            expires_at=None,
        )

        db.add(session)
        await db.flush()

        print("ChatSession created:")
        print("  database id:", session.id)
        print("  session_id:", session.session_id)

        # ---------------------------------------------------------
        # 2. Save user message
        # ---------------------------------------------------------

        user_message = ChatMessage(
            session_id=session.id,
            user_id="test-user",
            role="user",
            content="How many days of medical leave?",
            language="en",
            source="user",
        )

        db.add(user_message)

        # ---------------------------------------------------------
        # 3. Save assistant message
        # ---------------------------------------------------------

        assistant_message = ChatMessage(
            session_id=session.id,
            user_id="test-user",
            role="assistant",
            content="Employees are entitled to 12 days of medical leave per year.",
            language="en",
            source="Internal Knowledge",
            citations=[
                {
                    "source": "employee_leave_policy.pdf",
                    "page": 1,
                }
            ],
        )

        db.add(assistant_message)

        await db.commit()

        print("User message saved:", user_message.id)
        print("Assistant message saved:", assistant_message.id)

        # ---------------------------------------------------------
        # 4. Read conversation history
        # ---------------------------------------------------------

        result = await db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session.id)
            .order_by(ChatMessage.created_at.asc())
        )

        messages = result.scalars().all()

        print("\nConversation history:")
        print("=" * 60)

        for message in messages:
            print(
                f"{message.role.upper()}: "
                f"{message.content}"
            )

        print("=" * 60)

        # ---------------------------------------------------------
        # 5. Verify
        # ---------------------------------------------------------

        assert len(messages) == 2

        assert messages[0].role == "user"
        assert messages[1].role == "assistant"

        assert messages[0].content == (
            "How many days of medical leave?"
        )

        assert messages[1].content == (
            "Employees are entitled to 12 days of medical leave per year."
        )

        print("\nDatabase chat-history test PASSED.")

        # ---------------------------------------------------------
        # 6. Cleanup
        # ---------------------------------------------------------

        await db.delete(session)
        await db.commit()

        print("Test data cleaned up.")


if __name__ == "__main__":
    asyncio.run(test_db())
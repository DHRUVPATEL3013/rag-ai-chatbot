"""
SQLAlchemy models for Postgres.

Vectors live in Chroma — this database is for everything relational:
chat history, feedback, and the admin review queue (Phase 5 + 6).
"""

# TODO: define SQLAlchemy models, roughly:
#
# class ChatMessage:
#     id, session_id, user_id, role ("user"/"assistant"), content,
#     language, source ("Internal Knowledge" / "General AI Answer"),
#     created_at
#
# class Feedback:
#     id, message_id (FK -> ChatMessage), rating ("up"/"down"), created_at
#
# class ReviewQueueItem:
#     id, question, language, ai_answer, status ("pending"/"approved"/"rejected"),
#     created_at, reviewed_by, reviewed_at
#
# class PopularQuery:
#     id, query_text, hit_count   # backs Phase 6 search suggestions




"""
SQLAlchemy database models.

PostgreSQL stores relational application data.

ChromaDB remains responsible for:
- document chunks
- embeddings
- vector search

PostgreSQL is responsible for:
- chat sessions
- chat messages
- feedback
- admin review queue
- popular queries
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from sqlalchemy.dialects.postgresql import JSONB

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """

    pass


class ChatSession(Base):
    """
    Represents one conversation/session.

    A session contains multiple ChatMessage records.
    """

    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    conversation_summary: Mapped[str | None] = mapped_column(
    Text,
    nullable=True,
    )   

    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """
    One user or assistant message inside a chat session.
    """

    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chat_sessions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    citations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    session: Mapped["ChatSession"] = relationship(
        "ChatSession",
        back_populates="messages",
    )

    feedback: Mapped["Feedback | None"] = relationship(
        "Feedback",
        back_populates="message",
        uselist=False,
        cascade="all, delete-orphan",
    )

    previous_message_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "chat_messages.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    previous_message: Mapped["ChatMessage | None"] = relationship(
        "ChatMessage",
        remote_side="ChatMessage.id",
        foreign_keys=[previous_message_id],
    )



class Feedback(Base):
    """
    User feedback for an assistant message.

    rating:
        up
        down
    """

    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    message_id: Mapped[int] = mapped_column(
        ForeignKey(
            "chat_messages.id",
            ondelete="CASCADE",
        ),
        unique=True,
        nullable=False,
        index=True,
    )

    rating: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    message: Mapped["ChatMessage"] = relationship(
        "ChatMessage",
        back_populates="feedback",
    )


class ReviewQueueItem(Base):
    """
    Stores answers generated by external AI.

    Admin can:
        pending -> approved
        pending -> rejected

    Approved answers can later be added to ChromaDB.
    """

    __tablename__ = "review_queue_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    ai_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    improved_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    reviewed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    chat_session_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "chat_sessions.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    user_message_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "chat_messages.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    assistant_message_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "chat_messages.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        unique=True,
        index=True,
    )


class PopularQuery(Base):
    """
    Stores frequently asked questions.

    Used later for search suggestions.
    """

    __tablename__ = "popular_queries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    query_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )

    hit_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "query_text",
            "language",
            name="uq_popular_query_language",
        ),
    )
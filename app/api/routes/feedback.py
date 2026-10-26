"""
Feedback API endpoints.

Stores feedback for assistant messages.

Negative feedback is also added to the admin review queue.
"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    ChatMessage,
    Feedback,
    ReviewQueueItem,
)
from app.db.session import get_db


router = APIRouter(
    prefix="/feedback",
    tags=["Feedback"],
)


class FeedbackRequest(BaseModel):
    message_id: int
    rating: Literal["up", "down"]


@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Save feedback for an assistant message.

    If the rating is "down", also create a review queue item.
    """

    # -----------------------------------------------------
    # 1. Find assistant message
    # -----------------------------------------------------

    result = await db.execute(
        select(ChatMessage).where(
            ChatMessage.id == request.message_id
        )
    )

    assistant_message = result.scalar_one_or_none()

    if assistant_message is None:
        raise HTTPException(
            status_code=404,
            detail="Message not found.",
        )

    if assistant_message.role != "assistant":
        raise HTTPException(
            status_code=400,
            detail=(
                "Feedback can only be submitted "
                "for assistant messages."
            ),
        )

    # -----------------------------------------------------
    # 2. Find existing feedback
    # -----------------------------------------------------

    result = await db.execute(
        select(Feedback).where(
            Feedback.message_id == request.message_id
        )
    )

    existing_feedback = result.scalar_one_or_none()

    if existing_feedback is not None:

        # User is changing their vote.
        existing_feedback.rating = request.rating

    else:

        # First feedback for this message.
        feedback = Feedback(
            message_id=request.message_id,
            rating=request.rating,
        )

        db.add(feedback)

    # -----------------------------------------------------
    # 3. If negative feedback, create review queue item
    # -----------------------------------------------------


    if request.rating == "down":

        user_message = None

        if assistant_message.previous_message_id:
            result = await db.execute(
                select(ChatMessage).where(
                    ChatMessage.id
                    == assistant_message.previous_message_id
                )
            )

            user_message = result.scalar_one_or_none()

        if user_message is not None:

            result = await db.execute(
                select(ReviewQueueItem).where(
                    ReviewQueueItem.assistant_message_id
                    == assistant_message.id
                )
            )

            existing_review = result.scalar_one_or_none()

            if existing_review is None:

                review_item = ReviewQueueItem(
                    question=user_message.content,
                    language=assistant_message.language,
                    ai_answer=assistant_message.content,
                    status="pending",
                    chat_session_id=assistant_message.session_id,
                    user_message_id=user_message.id,
                    assistant_message_id=assistant_message.id,
                )

                db.add(review_item)

    # -----------------------------------------------------
    # 4. Save everything
    # -----------------------------------------------------

    await db.commit()

    return {
        "success": True,
        "message_id": request.message_id,
        "rating": request.rating,
        "message": "Feedback submitted successfully.",
    }
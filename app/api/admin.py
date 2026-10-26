"""
Admin review endpoints — Phase 5.
"""

# TODO: FastAPI APIRouter with:
#
#   GET /admin/review-queue
#     -> list pending ReviewQueueItem rows
#
#   POST /admin/review-queue/{id}/approve
#     -> chunk + embed the (possibly admin-edited) answer via
#        ingestion.embed_store.add_documents(), tag category="AI-Improved",
#        mark the item "approved"
#
#   POST /admin/review-queue/{id}/reject
#     -> mark the item "rejected", no re-ingestion
# =========
from langchain_core.documents import Document
from reportlab.lib.pagesizes import A4
from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import secrets

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Request,
    Depends,
)

from fastapi.responses import (
    RedirectResponse,
    JSONResponse,
)

from pydantic import BaseModel

from sqlalchemy import (
    select,
    func,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

from app.db.models import ReviewQueueItem

from app.db.session import get_db

from app.ingestion.chunking import split_general_text
from app.ingestion.embed_store import add_documents, get_vectorstore
from app.ingestion.language_detect import detect_language
from app.ingestion.loaders import load_by_extension

# ===========


from datetime import datetime, timedelta, timezone
from pathlib import Path
import hashlib
import secrets

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.config import settings
from app.ingestion.chunking import split_general_text
from app.ingestion.embed_store import add_documents, get_vectorstore
from app.ingestion.language_detect import detect_language
from app.ingestion.loaders import load_by_extension

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".xlsx",
    ".png",
    ".jpg",
    ".jpeg",
}


# In-memory sessions for now.
# Restarting the server clears all sessions.
sessions = {}


def calculate_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def document_already_exists(file_hash: str) -> bool:
    vectorstore = get_vectorstore()

    result = vectorstore._collection.get(
        where={
            "file_hash": file_hash
        },
        include=["metadatas"],
    )

    return bool(result.get("metadatas"))


def create_session() -> str:
    token = secrets.token_urlsafe(32)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(minutes=settings.ADMIN_SESSION_MINUTES)
    )

    sessions[token] = expires_at

    return token


def validate_session(request: Request) -> bool:
    token = request.cookies.get("admin_session")

    if not token:
        return False

    expires_at = sessions.get(token)

    if not expires_at:
        return False

    if datetime.now(timezone.utc) >= expires_at:
        sessions.pop(token, None)
        return False

    return True


@router.get("/login")
async def login_page():
    return RedirectResponse("/admin/login.html")


@router.post("/login")
async def login(request: Request):

    data = await request.json()

    username = data.get("username")
    password = data.get("password")

    if (
        username != settings.ADMIN_USERNAME
        or password != settings.ADMIN_PASSWORD
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password.",
        )

    session_token = create_session()

    response = {
        "status": "success",
        "message": "Login successful.",
    }

    from fastapi.responses import JSONResponse

    json_response = JSONResponse(response)

    json_response.set_cookie(
        key="admin_session",
        value=session_token,
        max_age=settings.ADMIN_SESSION_MINUTES * 60,
        httponly=True,
        samesite="lax",
    )

    return json_response


@router.post("/logout")
async def logout(request: Request):

    token = request.cookies.get("admin_session")

    if token:
        sessions.pop(token, None)

    from fastapi.responses import JSONResponse

    response = JSONResponse(
        {
            "status": "success",
            "message": "Logged out.",
        }
    )

    response.delete_cookie("admin_session")

    return response


@router.get("/session")
async def check_session(request: Request):

    if not validate_session(request):
        raise HTTPException(
            status_code=401,
            detail="Admin session expired.",
        )

    return {
        "authenticated": True,
        "expires_in_minutes": settings.ADMIN_SESSION_MINUTES,
    }


@router.post("/upload")
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
):

    if not validate_session(request):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required or session expired.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported file type: {extension}. "
                f"Supported types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
            ),
        )

    filename = Path(file.filename).name

    destination = UPLOAD_DIR / filename

    with open(destination, "wb") as output:
        while chunk := await file.read(1024 * 1024):
            output.write(chunk)

    file_hash = calculate_file_hash(destination)

    # Do not ingest the same document twice.
    if document_already_exists(file_hash):
        return {
            "status": "already_exists",
            "filename": filename,
            "chunks_added": 0,
            "message": "This document already exists in the knowledge base.",
        }

    try:
        documents = load_by_extension(
            str(destination)
        )

    except Exception as exc:

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=500,
            detail=f"Failed to read document: {exc}",
        )

    if not documents:

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="No readable content was found in the document.",
        )

    for document in documents:

        document.metadata["language"] = detect_language(
            document.page_content
        )

        document.metadata["file_hash"] = file_hash
        document.metadata["filename"] = filename

    chunks = split_general_text(documents)

    if not chunks:

        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="No chunks were created from the document.",
        )

    for chunk in chunks:

        chunk.metadata["file_hash"] = file_hash
        chunk.metadata["filename"] = filename

    add_documents(chunks)

    return {
        "status": "success",
        "filename": filename,
        "documents_loaded": len(documents),
        "chunks_added": len(chunks),
        "message": "Document added to the knowledge base successfully.",
    }




##################################

@router.get("/review-queue")
async def get_review_queue(
    request: Request,
    db: AsyncSession = Depends(get_db),
    page: int = 1,
    page_size: int = 1,
    status: str = "pending",
):
    """
    Return paginated admin review queue items.
    """

    # -----------------------------------------------------
    # 1. Check admin authentication
    # -----------------------------------------------------

    if not validate_session(request):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required or session expired.",
        )

    # -----------------------------------------------------
    # 2. Validate pagination
    # -----------------------------------------------------

    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="page must be >= 1.",
        )

    if page_size < 1 or page_size > 100:
        raise HTTPException(
            status_code=400,
            detail="page_size must be between 1 and 100.",
        )

    # -----------------------------------------------------
    # 3. Validate status
    # -----------------------------------------------------

    allowed_statuses = {
        "pending",
        "approved",
        "rejected",
        "all",
    }

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=(
                "status must be one of: "
                "pending, approved, rejected, all."
            ),
        )

    # -----------------------------------------------------
    # 4. Build query
    # -----------------------------------------------------

    query = select(ReviewQueueItem)

    count_query = select(
        func.count(ReviewQueueItem.id)
    )

    if status != "all":

        query = query.where(
            ReviewQueueItem.status == status
        )

        count_query = count_query.where(
            ReviewQueueItem.status == status
        )

    # -----------------------------------------------------
    # 5. Total count
    # -----------------------------------------------------

    count_result = await db.execute(count_query)

    total = count_result.scalar_one()

    # -----------------------------------------------------
    # 6. Pagination
    # -----------------------------------------------------

    offset = (page - 1) * page_size

    query = (
        query
        .order_by(
            ReviewQueueItem.created_at.desc()
        )
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)

    items = result.scalars().all()

    # -----------------------------------------------------
    # 7. Serialize
    # -----------------------------------------------------

    response_items = []

    for item in items:

        response_items.append(
            {
                "id": item.id,
                "question": item.question,
                "language": item.language,
                "ai_answer": item.ai_answer,
                "improved_answer": (
                    item.improved_answer
                    or ""
                ),
                "status": item.status,
                "reviewed_by": item.reviewed_by,
                "reviewed_at": item.reviewed_at,
                "created_at": item.created_at,
                "chat_session_id": item.chat_session_id,
                "user_message_id": item.user_message_id,
                "assistant_message_id": item.assistant_message_id,
            }
        )

    # -----------------------------------------------------
    # 8. Calculate pages
    # -----------------------------------------------------

    total_pages = (
        (total + page_size - 1) // page_size
        if total
        else 0
    )

    return {
        "items": response_items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "status": status,
    }


#----------------------------#

class ApproveReviewRequest(BaseModel):
    improved_answer: str




from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle


AI_IMPROVED_DIR = Path(
    "data/uploads/ai_improved"
)

AI_IMPROVED_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

AI_IMPROVED_PDF = (
    AI_IMPROVED_DIR
    / "ai_improved_knowledge.pdf"
)



def rebuild_ai_improved_pdf(items):
    """
    Rebuild the single curated AI-improved PDF
    from all approved review items.
    """

    document = SimpleDocTemplate(
        str(AI_IMPROVED_PDF),
        pagesize=A4,
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "AI Improved Company Knowledge",
            styles["Title"],
        )
    )

    story.append(
        Spacer(1, 20)
    )

    for item in items:

        story.append(
            Paragraph(
                f"Review #{item.id}",
                styles["Heading2"],
            )
        )

        story.append(
            Paragraph(
                "<b>Question</b>",
                styles["Heading3"],
            )
        )

        story.append(
            Paragraph(
                item.question,
                styles["BodyText"],
            )
        )

        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                "<b>Approved Answer</b>",
                styles["Heading3"],
            )
        )

        story.append(
            Paragraph(
                item.improved_answer or "",
                styles["BodyText"],
            )
        )

        story.append(
            Spacer(1, 20)
        )

    document.build(story)


def remove_existing_ai_improved(review_id: int):
    """
    Remove the previous Chroma representation
    of this review before re-embedding it.
    """

    vectorstore = get_vectorstore()

    vectorstore._collection.delete(
        where={
            "review_id": review_id
        }
    )



@router.post(
    "/review-queue/{review_id}/approve"
)
async def approve_review(
    review_id: int,
    request: Request,
    body: ApproveReviewRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Approve an admin-edited answer.

    Flow:

    PostgreSQL
        ->
    ChromaDB
        ->
    curated PDF
    """

    if not validate_session(request):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required or session expired.",
        )

    # -----------------------------------------------------
    # 1. Find review
    # -----------------------------------------------------

    result = await db.execute(
        select(ReviewQueueItem).where(
            ReviewQueueItem.id == review_id
        )
    )

    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Review item not found.",
        )

    # -----------------------------------------------------
    # 2. Validate answer
    # -----------------------------------------------------

    improved_answer = (
        body.improved_answer or ""
    ).strip()

    if not improved_answer:
        raise HTTPException(
            status_code=400,
            detail="Improved answer cannot be empty.",
        )

    # -----------------------------------------------------
    # 3. Update PostgreSQL
    # -----------------------------------------------------

    item.improved_answer = improved_answer

    item.status = "approved"

    item.reviewed_by = (
        settings.ADMIN_USERNAME
    )

    item.reviewed_at = (
        datetime.now(timezone.utc)
    )

    await db.flush()

    # -----------------------------------------------------
    # 4. Update Chroma                                      
    # -----------------------------------------------------

    try:

        remove_existing_ai_improved(
            item.id
        )

        document = Document(
            page_content=(
                f"Question:\n"
                f"{item.question}\n\n"
                f"Approved Answer:\n"
                f"{improved_answer}"
            ),
            metadata={
                "category": "AI-Improved",
                "review_id": item.id,
                "source": "admin_review",
                "filename": (
                    "ai_improved_knowledge.pdf"
                ),
                "user_message_id": (
                    item.user_message_id
                ),
                "assistant_message_id": (
                    item.assistant_message_id
                ),
            },
        )

        chunks = split_general_text(
            [document]
        )

        if not chunks:
            raise ValueError(
                "No chunks created."
            )

        for chunk in chunks:
            chunk.metadata[
                "category"
            ] = "AI-Improved"

            chunk.metadata[
                "review_id"
            ] = item.id

            chunk.metadata[
                "source"
            ] = "admin_review"

            chunk.metadata[
                "filename"
            ] = "ai_improved_knowledge.pdf"

        add_documents(chunks)

    except Exception as exc:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to update AI-improved "
                f"knowledge: {exc}"
            ),
        )

    # -----------------------------------------------------
    # 5. Rebuild curated PDF
    # -----------------------------------------------------

    try:

        approved_result = await db.execute(
            select(ReviewQueueItem)
            .where(
                ReviewQueueItem.status
                == "approved"
            )
            .order_by(
                ReviewQueueItem.id.asc()
            )
        )

        approved_items = (
            approved_result.scalars().all()
        )

        rebuild_ai_improved_pdf(
            approved_items
        )

    except Exception as exc:

        # The database/chroma approval has already
        # happened. PDF failure should be reported.
        raise HTTPException(
            status_code=500,
            detail=(
                "Review approved and indexed, "
                "but PDF generation failed: "
                f"{exc}"
            ),
        )

    await db.commit()

    return {
        "success": True,
        "review_id": item.id,
        "status": item.status,
        "improved_answer": item.improved_answer,
        "message": (
            "Review approved and added "
            "to AI-improved knowledge."
        ),
    }



@router.post(
    "/review-queue/{review_id}/reject"
)
async def reject_review(
    review_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Reject a review item.

    No Chroma or PDF update occurs.
    """

    if not validate_session(request):
        raise HTTPException(
            status_code=401,
            detail="Admin authentication required or session expired.",
        )

    result = await db.execute(
        select(ReviewQueueItem).where(
            ReviewQueueItem.id == review_id
        )
    )

    item = result.scalar_one_or_none()

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Review item not found.",
        )

    item.status = "rejected"

    item.reviewed_by = (
        settings.ADMIN_USERNAME
    )

    item.reviewed_at = (
        datetime.now(timezone.utc)
    )

    await db.commit()

    return {
        "success": True,
        "review_id": item.id,
        "status": "rejected",
        "message": (
            "Review rejected successfully."
        ),
    }
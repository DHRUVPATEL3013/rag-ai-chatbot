from pathlib import Path
import hashlib

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.ingestion.chunking import split_general_text
from app.ingestion.embed_store import add_documents, get_vectorstore
from app.ingestion.language_detect import detect_language
from app.ingestion.loaders import load_by_extension


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
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


def calculate_file_hash(file_path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while chunk := file.read(1024 * 1024):
            sha256.update(chunk)

    return sha256.hexdigest()


def document_already_exists(file_hash: str) -> bool:
    """
    Check whether a document with the same file hash
    already exists in ChromaDB.
    """

    vectorstore = get_vectorstore()

    result = vectorstore._collection.get(
        where={
            "file_hash": file_hash
        },
        include=["metadatas"],
    )

    return bool(result.get("metadatas"))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload and ingest a new document.

    Existing documents are not deleted or re-ingested.
    """

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

    # --------------------------------------------------
    # Save uploaded file
    # --------------------------------------------------

    destination = UPLOAD_DIR / filename

    with open(destination, "wb") as output:
        while chunk := await file.read(1024 * 1024):
            output.write(chunk)

    # --------------------------------------------------
    # Calculate hash
    # --------------------------------------------------

    file_hash = calculate_file_hash(destination)

    # --------------------------------------------------
    # Check duplicate
    # --------------------------------------------------

    if document_already_exists(file_hash):
        return {
            "status": "already_exists",
            "filename": filename,
            "chunks_added": 0,
            "message": "This document already exists in the knowledge base.",
        }

    # --------------------------------------------------
    # Load document
    # --------------------------------------------------

    try:
        documents = load_by_extension(str(destination))

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

    # --------------------------------------------------
    # Language detection
    # --------------------------------------------------

    for document in documents:
        language = detect_language(
            document.page_content
        )

        document.metadata["language"] = language

        # Store information needed for duplicate detection
        document.metadata["file_hash"] = file_hash
        document.metadata["filename"] = filename

    # --------------------------------------------------
    # Chunking
    # --------------------------------------------------

    chunks = split_general_text(documents)

    if not chunks:
        destination.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="No chunks were created from the document.",
        )

    # --------------------------------------------------
    # Preserve metadata on chunks
    # --------------------------------------------------

    for chunk in chunks:
        chunk.metadata["file_hash"] = file_hash
        chunk.metadata["filename"] = filename

    # --------------------------------------------------
    # Add ONLY the new chunks
    # --------------------------------------------------

    add_documents(chunks)

    return {
        "status": "success",
        "filename": filename,
        "documents_loaded": len(documents),
        "chunks_added": len(chunks),
        "message": "Document added to the knowledge base successfully.",
    }
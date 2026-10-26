"""
Ingestion endpoint — Phase 1 + 2, exposed as an API.
"""

# TODO: FastAPI APIRouter with:
#
#   POST /ingest
#     accepts a file upload + category
#     -> runs it through: ingestion.loaders -> ingestion.ocr (if needed)
#        -> ingestion.language_detect -> ingestion.chunking
#        -> ingestion.embed_store.add_documents
#
# For your first working version, scripts/ingest_documents.py (CLI) is
# faster to test with than building this endpoint + a file upload UI.

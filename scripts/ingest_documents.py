# """
# CLI helper to bulk-ingest a folder of documents.

# This is the fastest way to test the whole Phase 1+2 pipeline end to end
# before the API or UI exist — your Day 1-2 milestone.

# Usage:
#     python scripts/ingest_documents.py --folder data/sample_docs --category "HR"
# """

# from app.ingestion.chunking import split_general_text
# from app.ingestion.loaders import load_pdf
# from app.ingestion.language_detect import detect_language

# from app.ingestion.embed_store import add_documents

# PDF_PATH = "data/sample_docs/employee_leave_policy.pdf"


# documents = load_pdf(PDF_PATH)

# print(f"Number of documents: {len(documents)}")

# for index, document in enumerate(documents, start=1):
#     print(f"\n--- Document {index} ---")

#     print("\nPage Content:")
#     print(document.page_content)

#     print("\nMetadata:")
#     print(document.metadata)


# chunks = split_general_text(
#     documents,
#     chunk_size=700,
#     chunk_overlap=100,
# )

# print(f"\nNumber of chunks: {len(chunks)}")

# for index, chunk in enumerate(chunks, start=1):
#     print(f"\n--- Chunk {index} ---")

#     print("\nChunk Content:")
#     print(chunk.page_content)

#     print("\nChunk Metadata:")
#     print(chunk.metadata)


# for chunk in chunks:
#     chunk.metadata["language"] = detect_language(chunk.page_content)

# print(f"\nNumber of chunks: {len(chunks)}")

# for index, chunk in enumerate(chunks, start=1):
#     print(f"\n--- Chunk {index} ---")

#     print("\nChunk Content:")
#     print(chunk.page_content)

#     print("\nChunk Metadata:")
#     print(chunk.metadata)


# add_documents(chunks)

# print(f"Stored {len(chunks)} chunks in ChromaDB.")



"""
CLI helper to bulk-ingest a folder of documents.

Usage:
    python -m scripts.ingest_documents
"""

import os

from app.ingestion.chunking import split_general_text
from app.ingestion.embed_store import add_documents
from app.ingestion.language_detect import detect_language
from app.ingestion.loaders import load_by_extension


FOLDER_PATH = "data/sample_docs"


total_files = 0
total_documents = 0
total_chunks = 0


for root, _, files in os.walk(FOLDER_PATH):
    for filename in files:
        file_path = os.path.join(root, filename)

        try:
            documents = load_by_extension(file_path)

            print(f"\nProcessing: {filename}")
            print(f"Documents loaded: {len(documents)}")

            for document in documents:
                language = detect_language(document.page_content)
                document.metadata["language"] = language

            chunks = split_general_text(documents)

            print(f"Chunks created: {len(chunks)}")

            add_documents(chunks)

            total_files += 1
            total_documents += len(documents)
            total_chunks += len(chunks)

        except Exception as exc:
            print(f"Failed to process {filename}: {exc}")


print("\n" + "=" * 50)
print("INGESTION SUMMARY")
print("=" * 50)
print(f"Files processed: {total_files}")
print(f"Documents loaded: {total_documents}")
print(f"Chunks stored: {total_chunks}")
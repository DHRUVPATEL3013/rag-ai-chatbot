# # """
# # Chunking — Phase 2. Splits loaded Documents into retrieval-sized chunks.
# # """


# # def split_general_text(documents: list, chunk_size: int = 700, chunk_overlap: int = 100) -> list:
# #     """
# #     TODO: Use langchain_text_splitters.RecursiveCharacterTextSplitter to
# #     split `documents` into smaller Document chunks. Every chunk must keep
# #     the original document's metadata (source, category, language) plus
# #     its own page number if available.
# #     """
# #     raise NotImplementedError


# # def split_structured_text(documents: list) -> list:
# #     """
# #     TODO: Use langchain_text_splitters.MarkdownHeaderTextSplitter for
# #     content with clear headers (FAQs, API docs). Add the header path as
# #     a "section" metadata field — this is what powers source citations
# #     in Phase 3 ("show source document, page, and section").
# #     """
# #     raise NotImplementedError


# from langchain_text_splitters import RecursiveCharacterTextSplitter
# import json
# from pathlib import Path

# def split_general_text(
#     documents: list,
#     chunk_size: int = 700,
#     chunk_overlap: int = 100,
# ) -> list:
#     """
#     Split loaded Documents into smaller retrieval-sized chunks.
#     """
#     # MarkdownHeaderTextSplitter
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=chunk_size,
#         chunk_overlap=chunk_overlap,
#     )

#     chunks = text_splitter.split_documents(documents)

#     print("=" * 60)
#     print(f"[CHUNKING] Documents received : {len(documents)}")
#     print(f"[CHUNKING] Chunks created      : {len(chunks)}")
#     print("=" * 60)

#     # Save chunks for debugging
#     output_dir = Path("debug")
#     output_dir.mkdir(exist_ok=True)

#     output_file = output_dir / "chunks.json"

#     chunk_data = []

#     for i, chunk in enumerate(chunks):
#         item = {
#             "chunk_number": i + 1,
#             "content": chunk.page_content,
#             "metadata": chunk.metadata,
#         }

#         chunk_data.append(item)

#         # Print first few chunks only
#         if i < 5:
#             print(f"\n[CHUNK {i + 1}]")
#             print(f"Metadata: {chunk.metadata}")
#             print(f"Content:\n{chunk.page_content[:1000]}")
#             print("-" * 60)

#     with open(output_file, "w", encoding="utf-8") as f:
#         json.dump(chunk_data, f, ensure_ascii=False, indent=2, default=str)

#     print(f"[CHUNKING] Saved chunks to: {output_file}")
#     print(f"[CHUNKING] Total chunks saved: {len(chunk_data)}")

#     return chunks



















from langchain_text_splitters import RecursiveCharacterTextSplitter
import json
from pathlib import Path


def get_next_chunk_file(output_dir: Path) -> Path:
    """
    Return a new chunk filename without overwriting
    any existing chunk file.

    Example:
        chunks.json
        chunks1.json
        chunks2.json
        chunks3.json
    """

    base_file = output_dir / "chunks.json"

    # First file
    if not base_file.exists():
        return base_file

    # Find the next available chunksN.json
    counter = 1

    while True:
        candidate = output_dir / f"chunks{counter}.json"

        if not candidate.exists():
            return candidate

        counter += 1


def split_general_text(
    documents: list,
    chunk_size: int = 700,
    chunk_overlap: int = 100,
) -> list:
    """
    Split loaded Documents into smaller retrieval-sized chunks.

    Existing debug chunk files are never overwritten.
    A new chunks*.json file is created for every run.
    """

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunks = text_splitter.split_documents(documents)

    print("=" * 60)
    print(f"[CHUNKING] Documents received : {len(documents)}")
    print(f"[CHUNKING] Chunks created      : {len(chunks)}")
    print("=" * 60)

    # ---------------------------------------------------------
    # Save chunks for debugging
    # ---------------------------------------------------------

    output_dir = Path("debug")
    output_dir.mkdir(exist_ok=True)

    # IMPORTANT:
    # Find a new filename instead of overwriting chunks.json
    output_file = get_next_chunk_file(output_dir)

    chunk_data = []

    for i, chunk in enumerate(chunks):

        item = {
            "chunk_number": i + 1,
            "content": chunk.page_content,
            "metadata": chunk.metadata,
        }

        chunk_data.append(item)

        # Print first few chunks only
        if i < 5:
            print(f"\n[CHUNK {i + 1}]")
            print(f"Metadata: {chunk.metadata}")
            print(f"Content:\n{chunk.page_content[:1000]}")
            print("-" * 60)

    # ---------------------------------------------------------
    # Write to NEW file
    # ---------------------------------------------------------

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            chunk_data,
            f,
            ensure_ascii=False,
            indent=2,
            default=str,
        )

    print(f"[CHUNKING] Saved chunks to: {output_file}")
    print(f"[CHUNKING] Total chunks saved: {len(chunk_data)}")

    return chunks
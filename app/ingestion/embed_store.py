# # """
# # Embeddings + ChromaDB storage — Phase 2.

# # This is the last step of ingestion: turn chunks into vectors and persist
# # them. Once this works end to end, you have a searchable knowledge base.
# # """


# # def get_embedding_function():
# #     """
# #     TODO: Return a langchain_huggingface.HuggingFaceEmbeddings instance
# #     configured with settings.EMBEDDING_MODEL (from app/config.py).
# #     """
# #     raise NotImplementedError


# # def get_vectorstore():
# #     """
# #     TODO: Return a langchain_chroma.Chroma instance, using
# #     settings.CHROMA_PERSIST_DIR and settings.CHROMA_COLLECTION_NAME,
# #     with get_embedding_function() as its embedding function.
# #     """
# #     raise NotImplementedError


# # def add_documents(chunks: list):
# #     """
# #     TODO: Add `chunks` (Documents with metadata, from chunking.py) into
# #     the vectorstore from get_vectorstore(). Chroma persists automatically
# #     when given a persist_directory, but check the langchain-chroma docs
# #     for your installed version to confirm.
# #     """
# #     raise NotImplementedError







# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma

# from app.config import settings


# def get_embedding_function():
#     """
#     Return the configured HuggingFace embedding model.
#     """
#     return HuggingFaceEmbeddings(
#         model_name=settings.EMBEDDING_MODEL,
#     )


# def get_vectorstore():
#     """
#     Return the ChromaDB vector store configured for this application.
#     """
#     return Chroma(
#         collection_name=settings.CHROMA_COLLECTION_NAME,
#         persist_directory=settings.CHROMA_PERSIST_DIR,
#         embedding_function=get_embedding_function(),
#     )


# def add_documents(chunks: list):
#     """
#     Add document chunks to the Chroma vector store.
#     """
#     vectorstore = get_vectorstore()
#     vectorstore.add_documents(chunks)


from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from app.config import settings


@lru_cache(maxsize=1)
def get_embedding_function():
    """
    Return the configured HuggingFace embedding model.

    The embedding model is created once and reused.
    """
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL,
    )


@lru_cache(maxsize=1)
def get_vectorstore():
    """
    Return the ChromaDB vector store configured for this application.

    The vector store is created once and reused for the lifetime
    of the application process.
    """
    return Chroma(
        collection_name=settings.CHROMA_COLLECTION_NAME,
        persist_directory=settings.CHROMA_PERSIST_DIR,
        embedding_function=get_embedding_function(),
    )


def add_documents(chunks: list):
    """
    Add document chunks to the Chroma vector store.
    """
    print("=" * 60)
    print(f"[EMBEDDING] Number of chunks: {len(chunks)}")
    print("[EMBEDDING] Starting embedding generation...")
    print("=" * 60)
    vectorstore = get_vectorstore()
    batch_size = 100

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        print(
            f"[EMBEDDING] Processing "
            f"{i + 1}-{min(i + batch_size, len(chunks))} "
            f"of {len(chunks)}"
        )

        vectorstore.add_documents(batch)
    print("=" * 60)
    print("[EMBEDDING] Embedding generation completed.")
    print("[EMBEDDING] Chunks stored in Chroma.")
    print("=" * 60)
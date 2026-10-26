# """
# Document loaders — Phase 1 (Knowledge Collection).

# Each function should load one file and return a list of LangChain
# `Document` objects, with `metadata` populated: at minimum `source`
# (filename) and `category` (passed in by the caller).

# Relevant LangChain classes to look up before writing these:
# - langchain_community.document_loaders.PyPDFLoader
# - langchain_community.document_loaders.UnstructuredWordDocumentLoader
# - langchain_community.document_loaders.UnstructuredExcelLoader
# - langchain_community.document_loaders.UnstructuredImageLoader

# Start here first (Day 1 milestone) — get load_pdf() working end to end
# on one real file before writing the others.
# """


# def load_pdf(file_path: str, category: str) -> list:
#     """
#     TODO: Load a PDF with PyPDFLoader, attach `category` to every
#     resulting Document's metadata, and return the list.
#     """
#     raise NotImplementedError


# def load_word(file_path: str, category: str) -> list:
#     """TODO: same pattern for .docx using UnstructuredWordDocumentLoader."""
#     raise NotImplementedError


# def load_excel(file_path: str, category: str) -> list:
#     """TODO: same pattern for .xlsx using UnstructuredExcelLoader."""
#     raise NotImplementedError


# def load_image(file_path: str, category: str) -> list:
#     """
#     TODO: Load an image file. If the loader doesn't extract meaningful
#     text (common for scanned images), fall back to ocr.extract_text_from_image().
#     """
#     raise NotImplementedError


# def load_by_extension(file_path: str, category: str) -> list:
#     """
#     TODO: Dispatch to the right loader above based on file extension.
#     Used by scripts/ingest_documents.py to handle a folder of mixed files.
#     """
#     raise NotImplementedError


# from pathlib import Path

# from langchain_community.document_loaders import PyPDFLoader
# from app.ingestion.loaders import load_by_extension

# def load_pdf(file_path: str) -> list:
    
#     """Load a PDF and return LangChain Document objects."""
#     path = Path(file_path)

#     if not path.exists():
#         raise FileNotFoundError(f"File not found: {path}")

#     loader = PyPDFLoader(str(path))

#     documents = loader.load()

#     return documents


"""
Document loaders — Phase 1 (Knowledge Collection).
"""

# from pathlib import Path

# from langchain_community.document_loaders import PyPDFLoader

from pathlib import Path

import pandas as pd

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

from app.ingestion.ocr import ocr_scanned_pdf

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredImageLoader,
)


from app.ingestion.ocr import extract_text_from_image

# def load_pdf(file_path: str, category: str = None) -> list:
#     """
#     Load a PDF and return LangChain Document objects.
#     """

#     path = Path(file_path)

#     if not path.exists():
#         raise FileNotFoundError(f"File not found: {path}")

#     loader = PyPDFLoader(str(path))

#     documents = loader.load()

#     for document in documents:
#         document.metadata["source"] = str(path)

#         if category:
#             document.metadata["category"] = category

#     return documents


# def load_pdf(
#     file_path: str,
#     category: str = None,
# ) -> list:
#     """
#     Load a PDF.

#     Uses PyPDFLoader for normal PDFs.
#     Falls back to OCR when the PDF contains little or no text.
#     """

#     path = Path(file_path)

#     if not path.exists():
#         raise FileNotFoundError(f"File not found: {path}")

#     # 1. Try normal PDF text extraction
#     loader = PyPDFLoader(str(path))
#     documents = loader.load()

#     # 2. Check whether meaningful text was extracted
#     total_text = "\n".join(
#         document.page_content.strip()
#         for document in documents
#     )

#     if len(total_text.strip()) >= 20:
#         for document in documents:
#             document.metadata["source"] = str(path)

#             if category:
#                 document.metadata["category"] = category

#         return documents

#     # 3. Normal extraction failed → OCR fallback
#     print(f"Using OCR for scanned PDF: {path.name}")

#     ocr_text = ocr_scanned_pdf(str(path))

#     if not ocr_text.strip():
#         return []

#     # 4. Convert OCR output into a LangChain Document
#     document = Document(
#         page_content=ocr_text,
#         metadata={
#             "source": str(path),
#         },
#     )

#     if category:
#         document.metadata["category"] = category

#     return [document]


def load_pdf(
    file_path: str,
    category: str = None,
) -> list:
    """
    Load a PDF.

    Uses PyPDFLoader for normal PDFs.
    Falls back to OCR when the PDF contains little or no text.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    # 1. Try normal PDF text extraction
    loader = PyPDFLoader(str(path))
    documents = loader.load()

    # 2. Check whether meaningful text was extracted
    total_text = "\n".join(
        document.page_content.strip()
        for document in documents
    )

    if len(total_text.strip()) >= 20:
        for document in documents:
            document.metadata["source"] = str(path)

            if category:
                document.metadata["category"] = category

        return documents

    # 3. Normal extraction failed → OCR fallback
    print(f"Using OCR for scanned PDF: {path.name}")

    ocr_text = ocr_scanned_pdf(str(path))

    if not ocr_text.strip():
        return []

    # 4. Convert OCR output into a LangChain Document
    document = Document(
        page_content=ocr_text,
        metadata={
            "source": str(path),
        },
    )

    if category:
        document.metadata["category"] = category

    return [document]


def load_by_extension(
    file_path: str,
    category: str = None,
) -> list:
    """
    Select the appropriate loader based on the file extension.
    """

    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return load_pdf(file_path, category)

    if extension == ".docx":
        return load_word(file_path, category)

    if extension == ".xlsx":
        return load_excel(file_path, category)

    if extension in [".png", ".jpg", ".jpeg"]:
        return load_image(file_path, category)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )




def load_word(
    file_path: str,
    category: str = None,
) -> list:
    """Load a Word document."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    loader = UnstructuredWordDocumentLoader(str(path))
    documents = loader.load()

    for document in documents:
        document.metadata["source"] = str(path)

        if category:
            document.metadata["category"] = category

    return documents



def load_excel(
    file_path: str,
    category: str = None,
) -> list:
    """
    Load Excel sheets as row-aware LangChain Documents.

    Each row is converted into:
        Column: Value
        Column: Value
        ...

    This preserves the relationship between column names and values
    for semantic retrieval.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    print("=" * 60)
    print(f"[EXCEL] Loading: {path.name}")
    print("=" * 60)

    # Read all sheets
    sheets = pd.read_excel(
        path,
        sheet_name=None,
    )

    documents = []

    for sheet_name, dataframe in sheets.items():

        print(
            f"[EXCEL] Sheet: {sheet_name} | "
            f"Rows: {len(dataframe)} | "
            f"Columns: {len(dataframe.columns)}"
        )

        # Clean column names
        dataframe.columns = [
            str(column).strip()
            for column in dataframe.columns
        ]

        for row_number, row in dataframe.iterrows():

            lines = [
                f"Sheet: {sheet_name}",
                f"Row: {row_number + 2}",
            ]

            for column in dataframe.columns:

                value = row[column]

                # Handle NaN
                if pd.isna(value):
                    value = ""

                lines.append(
                    f"{column}: {value}"
                )

            document = Document(
                page_content="\n".join(lines),
                metadata={
                    "source": str(path),
                    "filename": path.name,
                    "sheet": str(sheet_name),
                    "row": int(row_number + 2),
                },
            )

            if category:
                document.metadata["category"] = category

            documents.append(document)

    print("-" * 60)
    print(f"[EXCEL] Total row documents: {len(documents)}")
    print("=" * 60)

    return documents



def load_image(file_path: str, category: str = None) -> list:
    """
    Load an image and extract its text.

    Uses UnstructuredImageLoader first. If it does not
    produce meaningful text, falls back to OCR.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    loader = UnstructuredImageLoader(str(path))
    documents = loader.load()

    # Check whether the loader extracted meaningful text
    text = "\n".join(
        document.page_content.strip()
        for document in documents
        if document.page_content.strip()
    )

    if len(text) < 20:
        ocr_text = extract_text_from_image(str(path))

        if not ocr_text.strip():
            return []

        documents = [
            Document(
                page_content=ocr_text,
                metadata={
                    "source": str(path),
                },
            )
        ]

    for document in documents:
        document.metadata["source"] = str(path)

        if category:
            document.metadata["category"] = category

    return documents
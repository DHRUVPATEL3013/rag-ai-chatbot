# """
# OCR fallback for scanned PDFs and images — Phase 2.

# Uses Tesseract via pytesseract, with eng+spa+fra language packs installed
# at the OS level (see README setup step 3).
# """


# def extract_text_from_image(image_path: str) -> str:
#     """
#     TODO: pytesseract.image_to_string(image, lang="eng+spa+fra")
#     Return the extracted text.
#     """
#     raise NotImplementedError


# def ocr_scanned_pdf(pdf_path: str) -> str:
#     """
#     TODO: Convert each page to an image with pdf2image.convert_from_path,
#     run extract_text_from_image() on each page, and concatenate the results.
#     Call this when load_pdf() returns pages with empty/near-empty text.
#     """
#     raise NotImplementedError






"""
OCR fallback for scanned PDFs and images.

Uses Tesseract via pytesseract.
"""

from pathlib import Path

import pytesseract
from pdf2image import convert_from_path


OCR_LANGUAGES = "eng+spa+fra"


def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from an image using Tesseract OCR.
    """

    text = pytesseract.image_to_string(
        image_path,
        lang=OCR_LANGUAGES,
    )

    return text.strip()


def ocr_scanned_pdf(pdf_path: str) -> str:
    """
    Convert each PDF page to an image and extract text using OCR.
    """

    pages = convert_from_path(pdf_path)

    extracted_text = []

    for page_number, page_image in enumerate(pages, start=1):
        text = pytesseract.image_to_string(
            page_image,
            lang=OCR_LANGUAGES,
        ).strip()

        if text:
            extracted_text.append(
                f"--- Page {page_number} ---\n{text}"
            )

    return "\n\n".join(extracted_text)
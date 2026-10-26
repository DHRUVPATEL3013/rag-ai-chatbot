
from app.ingestion.ocr import ocr_scanned_pdf


pdf_path = "data/sample_docs/scanned_employee_policy.pdf"

text = ocr_scanned_pdf(pdf_path)

print("=" * 60)
print("OCR RESULT")
print("=" * 60)
print(text)
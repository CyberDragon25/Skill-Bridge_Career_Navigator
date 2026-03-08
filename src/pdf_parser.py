from io import BytesIO
from pypdf import PdfReader


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    """
    Extract text from an uploaded PDF file in memory.
    """
    if not file_bytes:
        return ""

    reader = PdfReader(BytesIO(file_bytes))
    pages = []

    for page in reader.pages:
        try:
            text = page.extract_text() or ""
            if text.strip():
                pages.append(text)
        except Exception:
            continue

    return "\n\n".join(pages).strip()
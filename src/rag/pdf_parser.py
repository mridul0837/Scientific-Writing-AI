"""Extract text per page from an uploaded PDF."""

from pypdf import PdfReader


def parse_pdf(file_path: str) -> list[dict]:
    """Return a list of {"page": int, "text": str} for each non-empty page."""
    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page": i, "text": text})
    return pages

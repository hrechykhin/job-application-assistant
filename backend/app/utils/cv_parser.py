"""
CV text extraction utilities.
PDF support via pdfminer.six; DOCX support via python-docx.
"""

import logging
from io import BytesIO

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = {"application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB


def extract_text(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from a PDF or DOCX file."""
    lower = filename.lower()
    if lower.endswith(".pdf"):
        return _extract_pdf(file_bytes)
    if lower.endswith(".docx"):
        return _extract_docx(file_bytes)
    raise ValueError(f"Unsupported file type: {filename}")


def _extract_pdf(file_bytes: bytes) -> str:
    from pdfminer.high_level import extract_text as pdfminer_extract

    try:
        text = pdfminer_extract(BytesIO(file_bytes))
        return text.strip()
    except Exception as e:
        logger.error("PDF extraction failed: %s", e)
        raise ValueError("Could not extract text from PDF.") from e


def _extract_docx(file_bytes: bytes) -> str:
    from docx import Document

    try:
        doc = Document(BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        logger.error("DOCX extraction failed: %s", e)
        raise ValueError("Could not extract text from DOCX.") from e


def validate_upload(filename: str, content_type: str, size: int) -> None:
    """Raise ValueError if the file is not acceptable."""
    import os

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Only PDF and DOCX files are accepted. Got: {ext}")
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.")

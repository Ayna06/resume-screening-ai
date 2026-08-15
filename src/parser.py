"""
parser.py
Extracts raw text from resumes in PDF, DOCX, or TXT format.
"""

import io
import pdfplumber
from docx import Document


def extract_text_from_pdf(file) -> str:
    """Extract text from a PDF file-like object."""
    text_parts = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        return f"[ERROR] Could not read PDF: {e}"
    return "\n".join(text_parts).strip()


def extract_text_from_docx(file) -> str:
    """Extract text from a DOCX file-like object."""
    try:
        doc = Document(file)
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as e:
        return f"[ERROR] Could not read DOCX: {e}"


def extract_text_from_txt(file) -> str:
    """Extract text from a plain text file-like object."""
    try:
        raw = file.read()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="ignore")
        return raw.strip()
    except Exception as e:
        return f"[ERROR] Could not read TXT: {e}"


def extract_text(file, filename: str) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    `file` should be a file-like object (e.g. from Streamlit's file_uploader,
    or a standard Python file handle opened in binary mode).
    """
    filename = filename.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file)
    elif filename.endswith(".txt"):
        return extract_text_from_txt(file)
    else:
        return "[ERROR] Unsupported file type. Please upload a PDF, DOCX, or TXT file."


def is_extraction_valid(text: str) -> bool:
    """
    Basic sanity check: flags empty extraction or scanned/image-only PDFs
    (which pdfplumber cannot OCR).
    """
    if not text or text.startswith("[ERROR]"):
        return False
    if len(text.strip()) < 30:
        return False
    return True

"""
Document loading and text extraction.
Supports PDF, plain text, and images (basic).
"""

import os
import pdfplumber
from typing import Tuple
from pathlib import Path

try:
    import pymupdf as fitz
except ImportError:
    import fitz  # type: ignore


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF with pdfplumber fallback."""
    text_parts = []
    
    try:
        doc = fitz.open(file_path)
        for page in doc:
            text_parts.append(page.get_text("text"))
        doc.close()
        text = "\n".join(text_parts).strip()
        if len(text) > 50:
            return text
    except Exception as e:
        print(f"PyMuPDF failed: {e}")

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts).strip()
    except Exception as e:
        print(f"pdfplumber failed: {e}")
        return ""


def extract_text_from_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def process_document(file_path: str) -> Tuple[str, str]:
    """
    Process uploaded file and return (text, doc_type).
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == ".pdf":
        text = extract_text_from_pdf(file_path)
        return text, "pdf"
    elif suffix in [".txt", ".md", ".csv"]:
        text = extract_text_from_txt(file_path)
        return text, "text"
    else:
        # Try as text
        try:
            text = extract_text_from_txt(file_path)
            return text, "text"
        except Exception:
            return "", "unknown"

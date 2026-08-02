"""
PDF Utility Functions for CurricuAlign AI Academic Engine.

Provides multi-engine text extraction: PyMuPDF (fitz) -> pdfplumber -> raw PDF text stream parsing fallback.
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Union

logger = logging.getLogger("academic_engine.utils.pdf_utils")

# Check PyMuPDF
_FITZ_AVAILABLE = False
try:
    import fitz
    _FITZ_AVAILABLE = True
except ImportError:
    _FITZ_AVAILABLE = False

# Check pdfplumber
_PDFPLUMBER_AVAILABLE = False
try:
    import pdfplumber
    _PDFPLUMBER_AVAILABLE = True
except ImportError:
    _PDFPLUMBER_AVAILABLE = False


def extract_text_from_pdf(
    file_source: Union[str, Path, bytes]
) -> Tuple[str, List[str], str]:
    """
    Extract text and per-page text list from a PDF file path or bytes.

    Returns:
        Tuple of (full_text_string, list_of_page_text_strings, extractor_engine_name).
    """
    if isinstance(file_source, (str, Path)):
        path = Path(file_source)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found at: {path}")
        pdf_bytes = path.read_bytes()
    else:
        pdf_bytes = file_source

    # Engine 1: PyMuPDF (fitz)
    if _FITZ_AVAILABLE:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_text = []
            for page in doc:
                pages_text.append(page.get_text())
            full_text = "\n\n".join(pages_text)
            if full_text.strip():
                logger.info("[PDF] Extracted text using PyMuPDF (%d pages).", len(pages_text))
                return full_text, pages_text, "PyMuPDF"
        except Exception as exc:
            logger.warning("[PDF] PyMuPDF extraction failed: %s. Trying fallback.", exc)

    # Engine 2: pdfplumber
    if _PDFPLUMBER_AVAILABLE:
        try:
            import io
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
                full_text = "\n\n".join(pages_text)
                if full_text.strip():
                    logger.info("[PDF] Extracted text using pdfplumber (%d pages).", len(pages_text))
                    return full_text, pages_text, "pdfplumber"
        except Exception as exc:
            logger.warning("[PDF] pdfplumber extraction failed: %s.", exc)

    # Engine 3: Pure Python stream text extractor fallback
    pages_text, full_text = _extract_raw_pdf_text_fallback(pdf_bytes)
    logger.info("[PDF] Extracted text using fallback stream parser (%d pages).", len(pages_text))
    return full_text, pages_text, "FallbackStreamParser"


def _extract_raw_pdf_text_fallback(pdf_bytes: bytes) -> Tuple[List[str], str]:
    """
    Fallback text extractor for raw PDF byte streams.
    Extracts text objects enclosed in BT ... ET operators or raw strings.
    """
    text_content = []
    # Search for text stream chunks between BT (Begin Text) and ET (End Text)
    bt_et_matches = re.findall(rb"BT[\s\S]*?ET", pdf_bytes)

    if bt_et_matches:
        for chunk in bt_et_matches:
            # Extract strings inside ( ... ) or < ... >
            str_matches = re.findall(rb"\((.*?)\)", chunk)
            for sm in str_matches:
                try:
                    decoded = sm.decode("utf-8", errors="ignore").strip()
                    if len(decoded) > 1:
                        text_content.append(decoded)
                except Exception:
                    continue

    if not text_content:
        # Generic ASCII/UTF-8 string extraction fallback
        raw_strs = re.findall(rb"[A-Za-z0-9\s.,;:\-()\/\'\"]{4,}", pdf_bytes)
        for rs in raw_strs:
            decoded = rs.decode("utf-8", errors="ignore").strip()
            if len(decoded) > 3 and not decoded.startswith("PDF") and not decoded.startswith("obj"):
                text_content.append(decoded)

    full_text = "\n".join(text_content)
    pages = [full_text] if full_text else [""]
    return pages, full_text

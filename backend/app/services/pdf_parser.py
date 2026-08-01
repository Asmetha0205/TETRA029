import re
import os
from typing import List, Dict, Any

def parse_pdf_bytes(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Parses PDF bytes using PyMuPDF (fitz) with pdfplumber fallback.
    Extracts text and splits into syllabus units/modules.
    """
    extracted_text = ""
    
    # Primary parser: PyMuPDF (fitz)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages_text = []
        for page in doc:
            pages_text.append(page.get_text())
        extracted_text = "\n".join(pages_text)
    except Exception as e:
        # Fallback parser: pdfplumber
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                pages_text = [page.extract_text() or "" for page in pdf.pages]
                extracted_text = "\n".join(pages_text)
        except Exception as e_inner:
            extracted_text = f"Error extracting text from PDF: {str(e_inner)}"

    units = split_into_units(extracted_text)
    
    return {
        "filename": filename,
        "character_count": len(extracted_text),
        "extracted_text": extracted_text,
        "unit_count": len(units),
        "units": units
    }

def split_into_units(text: str) -> List[Dict[str, Any]]:
    """
    Splits syllabus text into logical units or modules using regex heuristics.
    """
    if not text.strip():
        return [{
            "unit_id": "unit_1",
            "title": "General Course Content",
            "text": "",
            "extracted_skills": []
        }]

    # Regex pattern matching 'Unit I', 'Unit 1', 'Module 1', 'Section 1', 'Chapter 1'
    unit_pattern = re.compile(
        r'(?i)(^(?:UNIT|MODULE|SECTION|CHAPTER)\s+[IVX0-9]+[^\n]*)', 
        re.MULTILINE
    )
    
    matches = list(unit_pattern.finditer(text))
    
    if not matches:
        # If no explicit Unit headers found, chunk by double linebreaks or paragraph clusters
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        units = []
        chunk_size = max(1, len(paragraphs) // 4)
        for idx in range(0, len(paragraphs), chunk_size):
            chunk_paras = paragraphs[idx:idx + chunk_size]
            unit_num = (idx // chunk_size) + 1
            units.append({
                "unit_id": f"unit_{unit_num}",
                "title": f"Module {unit_num}: " + (chunk_paras[0][:40] + "..." if chunk_paras else "Section"),
                "text": "\n\n".join(chunk_paras),
                "extracted_skills": []
            })
        return units if units else [{
            "unit_id": "unit_1",
            "title": "Module 1: General Syllabus",
            "text": text,
            "extracted_skills": []
        }]
    
    units = []
    for i in range(len(matches)):
        start_pos = matches[i].start()
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        
        header = matches[i].group(1).strip()
        unit_content = text[start_pos:end_pos].strip()
        
        units.append({
            "unit_id": f"unit_{i + 1}",
            "title": header,
            "text": unit_content,
            "extracted_skills": []
        })
        
    return units

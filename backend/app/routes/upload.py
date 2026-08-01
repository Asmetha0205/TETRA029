from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
from ..services.pdf_parser import parse_pdf_bytes, split_into_units
from ..models.schemas import UploadResponse, SyllabusUnit

router = APIRouter(tags=["Stage 1 - Ingestion"])

@router.post("/upload", response_model=UploadResponse)
async def upload_syllabus(
    file: Optional[UploadFile] = File(None),
    raw_text: Optional[str] = Form(None)
):
    """
    Stage 1 — Ingestion: Accepts uploaded PDF or raw text syllabus,
    extracts text using PyMuPDF/pdfplumber, and splits into units/modules.
    """
    if file:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported for upload.")
        
        content = await file.read()
        parsed_result = parse_pdf_bytes(content, file.filename)
        
        unit_objs = [
            SyllabusUnit(
                unit_id=u["unit_id"],
                title=u["title"],
                text=u["text"],
                extracted_skills=u.get("extracted_skills", [])
            )
            for u in parsed_result["units"]
        ]
        
        return UploadResponse(
            status="uploaded",
            filename=file.filename,
            character_count=parsed_result["character_count"],
            unit_count=parsed_result["unit_count"],
            units=unit_objs,
            raw_text_preview=parsed_result["extracted_text"][:500] + ("..." if len(parsed_result["extracted_text"]) > 500 else "")
        )
    
    elif raw_text:
        units = split_into_units(raw_text)
        unit_objs = [
            SyllabusUnit(
                unit_id=u["unit_id"],
                title=u["title"],
                text=u["text"],
                extracted_skills=u.get("extracted_skills", [])
            )
            for u in units
        ]
        return UploadResponse(
            status="processed",
            filename="text_input.txt",
            character_count=len(raw_text),
            unit_count=len(units),
            units=unit_objs,
            raw_text_preview=raw_text[:500] + ("..." if len(raw_text) > 500 else "")
        )
    
    else:
        raise HTTPException(status_code=400, detail="Please provide either a PDF file or raw_text input.")

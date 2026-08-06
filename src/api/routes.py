"""FastAPI router endpoints for Human Writing Engine."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from schemas.brief import ContentBriefModel
from schemas.document import DocumentModel
from src.ingestion.router import parse_document
from src.planner.brief_planner import prepare_plan_from_brief
from src.planner.outline_generator import generate_outline_document
from src.generation.variant_generator import generate_10_variants
from src.diversity.filter import filter_most_diverse_variants
from src.reconstruction.engine import reconstruct_article
from src.style.cliche_cleaner import clean_ai_cliches
from src.validation.engine import validate_article

router = APIRouter(prefix="/api/v1", tags=["humanize"])


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "Human Writing Engine API", "version": "1.0.0"}


@router.post("/humanize/brief")
async def humanize_from_brief(brief: ContentBriefModel) -> Dict[str, Any]:
    """Generate long-form publication-ready content from a brief (Mode B)."""
    try:
        doc = prepare_plan_from_brief(brief)
        doc = generate_outline_document(doc)
        variants = await generate_10_variants(doc)
        retained, div_report = filter_most_diverse_variants(variants, retain_count=7)
        reconstructed = reconstruct_article(retained, doc)
        reconstructed.raw_content = clean_ai_cliches(reconstructed.raw_content)
        val_report = validate_article(reconstructed, target_word_count=brief.target_word_count)

        return {
            "title": reconstructed.title,
            "word_count": reconstructed.total_word_count,
            "content_markdown": reconstructed.raw_content,
            "sections": [s.model_dump() for s in reconstructed.sections],
            "faqs": [f.model_dump() for f in reconstructed.faqs],
            "diversity_report": div_report.model_dump(),
            "validation_report": val_report.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/humanize/file")
async def humanize_from_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Humanize an existing document uploaded via multipart form (Mode A)."""
    try:
        content_bytes = await file.read()
        filename = file.filename or "upload.txt"

        if filename.endswith(".docx"):
            # Save temporary file for docx parser
            temp_path = f"/tmp/{filename}"
            with open(temp_path, "wb") as f:
                f.write(content_bytes)
            doc = parse_document(temp_path)
        else:
            text_str = content_bytes.decode("utf-8", errors="ignore")
            doc = parse_document(text_str)

        doc = generate_outline_document(doc)
        variants = await generate_10_variants(doc)
        retained, div_report = filter_most_diverse_variants(variants, retain_count=7)
        reconstructed = reconstruct_article(retained, doc)
        reconstructed.raw_content = clean_ai_cliches(reconstructed.raw_content)
        val_report = validate_article(reconstructed, target_word_count=doc.total_word_count)

        return {
            "title": reconstructed.title,
            "word_count": reconstructed.total_word_count,
            "content_markdown": reconstructed.raw_content,
            "diversity_report": div_report.model_dump(),
            "validation_report": val_report.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Author: Naisarg H.
File: routes/agent.py
Description: This file defines the API endpoints for the AI agent pipeline.
It handles uploading documents, extracting data, mapping to form fields,
generating filled PDFs, and regenerating them after user edits.
It also merges all individual forms into a single transfer packet.
"""
import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.agent_service import AgentService
from services.pdf_service import fill_all_hcd_templates, render_pdf_preview, merge_pdfs

router = APIRouter(prefix="/api", tags=["agent"])
agent_service = AgentService()

# Paths (resolve relative to project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATES_DIR = PROJECT_ROOT / "templates"
OUTPUT_DIR = PROJECT_ROOT / "backend" / "output"


@router.post("/extract")
async def extract_data(file: UploadFile = File(...)):
    """Receives a PDF, saves it temporarily, and sends it to the AI for extraction."""
    temp_path = None
    try:
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        data = agent_service.extract_data(temp_path)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/map")
async def map_fields(extracted_data: dict):
    """Takes the raw extracted data and asks the AI to map it to form fields."""
    try:
        data = agent_service.map_data(extracted_data)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_pdfs(mapping: dict):
    """Fills all three HCD forms, creates a merged packet, and returns previews."""
    try:
        generated = fill_all_hcd_templates(mapping, TEMPLATES_DIR, OUTPUT_DIR)

        # Create consolidated transfer packet
        all_paths = [g["path"] for g in generated]
        merge_pdfs(all_paths, OUTPUT_DIR / "full_transfer_packet.pdf")

        previews = {g["form"]: render_pdf_preview(g["path"]) for g in generated}
        return {
            "status": "success",
            "data": {
                "generated_files": generated,
                "previews": previews,
                "has_packet": True,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/regenerate")
async def regenerate_pdfs(payload: dict):
    """Re-fills forms after user edits and rebuilds the transfer packet."""
    mapping = payload.get("mapping", {})
    try:
        generated = fill_all_hcd_templates(mapping, TEMPLATES_DIR, OUTPUT_DIR)

        # Rebuild the packet
        all_paths = [g["path"] for g in generated]
        merge_pdfs(all_paths, OUTPUT_DIR / "full_transfer_packet.pdf")

        previews = {g["form"]: render_pdf_preview(g["path"]) for g in generated}
        return {
            "status": "success",
            "data": {
                "generated_files": generated,
                "previews": previews,
                "has_packet": True,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

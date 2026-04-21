"""
Author: Naisarg H.
File: routes/files.py
Description: This file manages file-related operations for the system. 
Its primary job is to serve the generated, filled PDF documents to the user 
when they click the download button in the dashboard interface.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/download", tags=["files"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "backend" / "output"

@router.get("/{form_key}")
async def download_pdf(form_key: str):
    path = OUTPUT_DIR / f"{form_key}_filled.pdf"
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(path), media_type="application/pdf", filename=f"{form_key}_filled.pdf")

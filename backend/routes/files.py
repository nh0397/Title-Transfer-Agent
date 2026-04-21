"""
Author: Naisarg H.
File: routes/files.py
Description: This file handles downloading the generated PDF documents.
It serves individual filled forms as well as the merged full transfer
packet when the user clicks download in the dashboard.
"""
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/download", tags=["files"])

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = PROJECT_ROOT / "backend" / "output"


@router.get("/{form_key}")
async def download_pdf(form_key: str):
    """
    Serves a filled PDF for download. If form_key is 'full_packet',
    it returns the merged transfer packet with all three forms combined.
    """
    if form_key == "full_packet":
        path = OUTPUT_DIR / "full_transfer_packet.pdf"
        filename = "HCD_Transfer_Packet.pdf"
    else:
        path = OUTPUT_DIR / f"{form_key}_filled.pdf"
        filename = f"{form_key}_filled.pdf"

    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(str(path), media_type="application/pdf", filename=filename)

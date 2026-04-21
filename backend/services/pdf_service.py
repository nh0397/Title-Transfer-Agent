"""
Author: Naisarg H.
File: services/pdf_service.py
Description: This service handles the "physical" manipulation of PDF documents. 
It performs two main tasks: converting PDF pages into images so the AI can 
"see" them, and programmatically writing data into the interactive fields 
of official government PDF templates.
"""
import base64
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF

def pdf_to_base64_images(pdf_path: str, max_pages: int = 1) -> list[str]:
    """
    Takes a PDF file and turns its pages into images. 
    This is necessary because the AI vision model needs to "see" the 
    document as a picture to read it.
    """
    doc = fitz.open(pdf_path)
    images = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img_bytes = pix.tobytes("png")
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append(b64)
    doc.close()
    return images

def render_pdf_preview(pdf_path: str) -> list[str]:
    """
    Creates a clear picture of a filled-out PDF page.
    This allows the user to see exactly what the final document 
    looks like directly in the web browser.
    """
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
        img_bytes = pix.tobytes("png")
        b64 = base64.b64encode(img_bytes).decode("utf-8")
        images.append(b64)
    doc.close()
    return images

def fill_single_pdf(template_path: Path, field_data: dict, output_path: Path) -> int:
    """
    Takes one blank government form and fills it with specific information.
    It carefully matches the names of the boxes in the PDF with the 
    data provided by the AI.
    """
    if not template_path.exists():
        return 0
        
    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    writer.append(reader)  # Preserves AcroForm

    filled = 0
    for field_name, value in field_data.items():
        if not value:
            continue
        for page in writer.pages:
            try:
                writer.update_page_form_field_values(page, {field_name: str(value)})
                filled += 1
                break
            except Exception:
                continue

    with open(output_path, "wb") as f:
        writer.write(f)

    return filled

def fill_all_hcd_templates(mapping: dict, templates_dir: Path, output_dir: Path) -> list[dict]:
    """
    The main coordinator for PDF filling. 
    It loops through the three different HCD forms (476.6G, 480.5, and 476.6)
    and ensures each one is populated with the correct data.
    """
    templates = {
        "hcd_476_6g": templates_dir / "hcd_476_6g.pdf",
        "hcd_480_5": templates_dir / "hcd_480_5.pdf",
        "hcd_476_6": templates_dir / "hcd_476_6.pdf",
    }

    generated_files = []
    for form_key, template_path in templates.items():
        if form_key not in mapping:
            continue

        output_path = output_dir / f"{form_key}_filled.pdf"
        field_data = mapping[form_key]
        filled = fill_single_pdf(template_path, field_data, output_path)

        generated_files.append({
            "form": form_key,
            "path": str(output_path),
            "fields_filled": filled,
        })

    return generated_files

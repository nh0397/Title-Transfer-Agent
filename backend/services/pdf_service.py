"""
Author: Naisarg H.
File: services/pdf_service.py
Description: This service does the hands-on work with PDF files. It converts
PDF pages into pictures so the AI can read them, fills in the blank boxes on
government forms with the extracted data, renders previews of the filled
forms, and merges all completed forms into a single transfer packet.
"""
import base64
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF


def pdf_to_base64_images(pdf_path: str, max_pages: int = 1) -> list[str]:
    """
    Turns a PDF page into an image so the AI vision model can read it.
    Returns the image as a base64-encoded string.
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
    Creates a picture of a filled PDF so the user can see exactly what
    it looks like inside the browser without downloading it.
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
    Takes one blank government form and writes the extracted data into
    the correct boxes. Returns how many boxes were successfully filled.
    """
    if not template_path.exists():
        return 0

    reader = PdfReader(str(template_path))
    writer = PdfWriter()
    writer.append(reader)  # Preserves AcroForm structure

    # Pre-fetch actual PDF field names to allow fuzzy matching
    actual_fields = {}
    pdf_fields = reader.get_fields()
    if pdf_fields:
        for k in pdf_fields.keys():
            normalized = k.replace(":", "").replace(" ", "").lower()
            actual_fields[normalized] = k

    filled = 0
    for field_name, value in field_data.items():
        if not value:
            continue
            
        # Fuzzy match LLM key against the actual PDF form field
        norm_key = str(field_name).replace(":", "").replace(" ", "").lower()
        target_key = actual_fields.get(norm_key, field_name)

        for page in writer.pages:
            try:
                writer.update_page_form_field_values(page, {target_key: str(value)})
            except Exception:
                continue
        filled += 1

    with open(output_path, "wb") as f:
        writer.write(f)

    return filled


def fill_all_hcd_templates(mapping: dict, templates_dir: Path, output_dir: Path) -> list[dict]:
    """
    Loops through all three HCD forms (476.6G, 480.5, 476.6) and fills
    each one with the mapped data. Returns a list of what was generated.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

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


def merge_pdfs(pdf_paths: list[str], output_path: Path):
    """
    Combines all individual filled PDFs into one single document.
    This creates the final transfer packet that can be printed or filed.
    """
    writer = PdfWriter()
    for path in pdf_paths:
        if Path(path).exists():
            reader = PdfReader(path)
            writer.append(reader)

    with open(output_path, "wb") as f:
        writer.write(f)
    return str(output_path)

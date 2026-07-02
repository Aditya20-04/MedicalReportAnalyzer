import fitz  # PyMuPDF
from PIL import Image
import io


def validate_file_size(file, max_size_mb: int) -> bool:
    """Check if uploaded file is within the allowed size limit."""
    file_size_mb = len(file.getvalue()) / (1024 * 1024)
    return file_size_mb <= max_size_mb


def extract_images_from_pdf(pdf_bytes: bytes, max_pages: int = 5):
    """
    Convert PDF pages into image parts for Gemini.
    Processes up to `max_pages` pages to avoid excessive API load.

    Returns:
        tuple: (list of image part dicts, total number of pages in PDF)
    """
    image_parts = []

    pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(pdf_doc)
    pages_to_process = min(total_pages, max_pages)

    for page_num in range(pages_to_process):
        page = pdf_doc.load_page(page_num)
        pix = page.get_pixmap(dpi=150)  # decent resolution for analysis
        image_data = pix.tobytes("png")

        image_parts.append({
            "mime_type": "image/png",
            "data": image_data,
            "page": page_num + 1
        })

    pdf_doc.close()
    return image_parts, total_pages


def prepare_image_part(file_bytes: bytes, mime_type: str) -> dict:
    """Wrap a raw image file into Gemini-compatible format."""
    return {
        "mime_type": mime_type,
        "data": file_bytes
    }


def get_image_preview(image_bytes: bytes) -> Image.Image:
    """Return a PIL Image object for Streamlit preview."""
    return Image.open(io.BytesIO(image_bytes))


def is_valid_pdf(pdf_bytes: bytes) -> bool:
    """Basic sanity check that the file is a readable PDF."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page_count = len(doc)
        doc.close()
        return page_count > 0
    except Exception:
        return False

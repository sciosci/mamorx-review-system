import fitz  # PyMuPDF
import io
from PIL import Image


def get_pdf_page_image(pdf_path, page_number, zoom=2):
    doc = fitz.open(pdf_path)
    if 0 <= page_number < len(doc):
        page = doc[page_number]
        mat = fitz.Matrix(zoom, zoom)  # Increase zoom factor for higher resolution
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        doc.close()

        # Convert bytes to PIL Image
        img = Image.open(io.BytesIO(img_bytes))
        return img
    else:
        doc.close()
        return None


def get_pdf_page_count(pdf_path):
    doc = fitz.open(pdf_path)
    page_count = len(doc)
    doc.close()
    return page_count

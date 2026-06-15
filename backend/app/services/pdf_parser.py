from pypdf import PdfReader

def parse_pdf(file_path: str) -> list[dict]:
    """
    Extracts text from a PDF, page by page.

    Returns a list of dicts, each representing one page:
    [{"page_number": 1, "text": "..."}, {"page_number": 2, "text": "..."}, ...]
    """
    reader = PdfReader(file_path)
    pages_data = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        pages_data.append({
            "page_number": page_number,
            "text": text
        })

    return pages_data

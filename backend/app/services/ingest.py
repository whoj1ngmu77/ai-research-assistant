from app.services.pdf_parser import parse_pdf
from app.services.chunker import chunk_pages
from app.services.embedder import embed_chunks
from app.services.vector_store import add_chunks


def ingest_pdf(file_path: str, document_id: str, user_id: str) -> int:
    """
    Runs the full ingest pipeline on a saved PDF:
    parse -> chunk -> embed -> store

    Returns the number of chunks created.
    """
    pages = parse_pdf(file_path)
    chunks = chunk_pages(pages, document_id, user_id)
    embedded_chunks = embed_chunks(chunks)
    add_chunks(embedded_chunks)

    return len(chunks)

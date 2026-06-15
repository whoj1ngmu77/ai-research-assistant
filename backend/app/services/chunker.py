from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def chunk_pages(pages_data: list[dict], document_id: str, user_id: str) -> list[dict]:
    """
    Splits page-level text into smaller overlapping chunks.

    Output: list of chunk dicts, each with text + metadata:
        [{"text": "...", "page_number": 1, "chunk_index": 0,
          "document_id": "...", "user_id": "..."}, ...]
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    all_chunks = []
    chunk_index = 0

    for page in pages_data:
        page_chunks = splitter.split_text(page["text"])

        for chunk_text in page_chunks:
            all_chunks.append({
                "text": chunk_text,
                "page_number": page["page_number"],
                "chunk_index": chunk_index,
                "document_id": document_id,
                "user_id": user_id,
            })
            chunk_index += 1

    return all_chunks

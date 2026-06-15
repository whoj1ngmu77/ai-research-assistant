import chromadb

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "documents"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)


def add_chunks(chunks: list[dict]):
    """
    Adds embedded chunks to ChromaDB.

    Each chunk dict must have:
        - text
        - embedding
        - document_id
        - page_number
        - chunk_index
    """
    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in chunks:
        chunk_id = f"{chunk['document_id']}_{chunk['chunk_index']}"

        ids.append(chunk_id)
        embeddings.append(chunk["embedding"])
        documents.append(chunk["text"])
        metadatas.append({
            "document_id": chunk["document_id"],
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"],
        })

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )


def get_collection_count() -> int:
    """Returns total number of chunks stored across all documents."""
    return collection.count()


def search(query_embedding: list[float], top_k: int = 4, document_ids: list[str] | None = None) -> list[dict]:
    """
    Finds the top_k most similar chunks to the query embedding.

    Args:
        query_embedding: embedding vector of the user's question
        top_k: how many results to return
        document_ids: optional list of document_ids to restrict the search to
                       (None = search across all uploaded documents)

    Returns: list of dicts:
        [{"text": "...", "page_number": 1, "document_id": "...", "distance": 0.23}, ...]
    """
    where_filter = None
    if document_ids:
        where_filter = {"document_id": {"$in": document_ids}}

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
    )

    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "text": results["documents"][0][i],
            "page_number": results["metadatas"][0][i]["page_number"],
            "document_id": results["metadatas"][0][i]["document_id"],
            "distance": results["distances"][0][i],
        })

    return chunks

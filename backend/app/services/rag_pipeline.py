from app.services.embedder import embed_text
from app.services.vector_store import search
from app.services.generator import generate_answer


def answer_question(question: str, document_ids: list[str] | None = None, top_k: int = 4) -> dict:
    """
    Runs the full RAG query pipeline:
    embed question -> retrieve chunks -> generate answer

    Returns: {"answer": str, "sources": list[dict]}
    """
    query_embedding = embed_text(question, task_type="RETRIEVAL_QUERY")
    chunks = search(query_embedding, top_k=top_k, document_ids=document_ids)
    answer = generate_answer(question, chunks)

    return {
        "answer": answer,
        "sources": chunks,
    }

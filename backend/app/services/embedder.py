from google import genai
from google.genai import types
from app.core.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"

def embed_text(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> list[float]:
    """
    Converts a single piece of text into an embedding vector.

    task_type:
        - "RETRIEVAL_DOCUMENT" for chunks being stored/searched
        - "RETRIEVAL_QUERY" for the user's question (used in Phase 8)
    """
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return result.embeddings[0].values


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """
    Adds an 'embedding' field to each chunk dict.
    """
    for chunk in chunks:
        chunk["embedding"] = embed_text(chunk["text"], task_type="RETRIEVAL_DOCUMENT")

    return chunks

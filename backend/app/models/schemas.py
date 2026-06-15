from pydantic import BaseModel


class UploadResponse(BaseModel):
    document_id: str
    original_filename: str
    chunks_created: int
    message: str


class ChatRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None
    top_k: int = 4


class SourceChunk(BaseModel):
    text: str
    page_number: int
    document_id: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]

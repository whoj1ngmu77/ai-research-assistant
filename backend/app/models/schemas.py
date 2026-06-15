from datetime import datetime
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
    session_id: str | None = None


class SourceChunk(BaseModel):
    text: str
    page_number: int
    document_id: str
    distance: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]
    session_id: str


class SessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    sources: list[SourceChunk] | None = None
    created_at: datetime

    class Config:
        from_attributes = True

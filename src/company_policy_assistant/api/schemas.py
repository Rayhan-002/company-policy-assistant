from datetime import date

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class CitationResponse(BaseModel):
    document_title: str
    version: str
    status: str
    section: str | None
    subsection: str | None


class ChatResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]


class DocumentResponse(BaseModel):
    document_id: str
    title: str
    version: str
    status: str
    category: str
    effective_from: date

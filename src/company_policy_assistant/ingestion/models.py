from datetime import date
from typing import Literal

from pydantic import BaseModel

Status = Literal["active", "archived"]


class DocumentMeta(BaseModel):
    document_id: str
    title: str
    version: str
    status: Status
    effective_from: date
    category: str
    supersedes: str | None = None
    superseded_by: str | None = None
    source_path: str


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    version: str
    status: Status
    effective_from: date
    category: str
    section_number: str | None
    section_name: str | None
    subsection_number: str | None
    subsection_name: str | None
    chunk_index: int
    text: str
    token_count: int

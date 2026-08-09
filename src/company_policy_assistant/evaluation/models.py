from pydantic import BaseModel


class GoldReference(BaseModel):
    document_id: str
    version: str
    section_name: str | None = None
    subsection_name: str | None = None


class BenchmarkQuestion(BaseModel):
    id: str
    category: str
    question: str
    gold_references: list[GoldReference] = []
    reference_answer: str | None = None
    expects_insufficient_evidence: bool = False
    notes: str | None = None

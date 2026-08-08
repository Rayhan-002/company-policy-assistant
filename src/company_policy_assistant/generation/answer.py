from dataclasses import dataclass

from ..retrieval import RetrievedChunk, Retriever
from .llm import LLMProvider
from .prompts import SYSTEM_PROMPT_TEMPLATE, build_user_prompt

DEFAULT_COMPANY_NAME = "Nexora Technologies"


@dataclass
class Citation:
    document_title: str
    version: str
    status: str
    section: str | None
    subsection: str | None
    chunk_id: str


@dataclass
class Answer:
    text: str
    citations: list[Citation]
    context_used: list[RetrievedChunk]


def _to_citation(result: RetrievedChunk) -> Citation:
    chunk = result.chunk
    return Citation(
        document_title=chunk.title,
        version=chunk.version,
        status=chunk.status,
        section=chunk.section_name,
        subsection=chunk.subsection_name,
        chunk_id=chunk.chunk_id,
    )


def answer_question(
    question: str,
    retriever: Retriever,
    llm: LLMProvider,
    *,
    top_k: int = 5,
    company_name: str = DEFAULT_COMPANY_NAME,
) -> Answer:
    results = retriever.retrieve(question, top_k=top_k)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(company=company_name)
    user_prompt = build_user_prompt(question, results)
    text = llm.generate(system_prompt, user_prompt)
    # Citations come from what was actually retrieved and passed as context, not parsed
    # from the model's own [n] markers — the model is instructed to only use this context,
    # so this list is guaranteed accurate rather than trusting a free-text citation claim.
    return Answer(text=text, citations=[_to_citation(r) for r in results], context_used=results)

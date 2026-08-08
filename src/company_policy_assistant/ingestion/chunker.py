import tiktoken

from .models import Chunk, DocumentMeta
from .parser import parse_markdown_body

_ENCODING = tiktoken.get_encoding("cl100k_base")
MAX_CHUNK_TOKENS = 300


def count_tokens(text: str) -> int:
    return len(_ENCODING.encode(text))


def _split_oversized(text: str, max_tokens: int) -> list[str]:
    """Split text on paragraph boundaries, packing paragraphs up to max_tokens."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    pieces: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}" if current else paragraph
        if current and count_tokens(candidate) > max_tokens:
            pieces.append(current)
            current = paragraph
        else:
            current = candidate
    if current:
        pieces.append(current)
    return pieces or [text]


def chunk_document(meta: DocumentMeta, body: str) -> list[Chunk]:
    chunks: list[Chunk] = []
    for node in parse_markdown_body(body):
        node_tokens = count_tokens(node.text)
        pieces = _split_oversized(node.text, MAX_CHUNK_TOKENS) if node_tokens > MAX_CHUNK_TOKENS else [node.text]
        for piece in pieces:
            chunks.append(
                Chunk(
                    chunk_id=f"{meta.document_id}__v{meta.version}__{len(chunks)}",
                    document_id=meta.document_id,
                    title=meta.title,
                    version=meta.version,
                    status=meta.status,
                    effective_from=meta.effective_from,
                    category=meta.category,
                    section_number=node.section_number,
                    section_name=node.section_name,
                    subsection_number=node.subsection_number,
                    subsection_name=node.subsection_name,
                    chunk_index=len(chunks),
                    text=piece,
                    token_count=count_tokens(piece),
                )
            )
    return chunks

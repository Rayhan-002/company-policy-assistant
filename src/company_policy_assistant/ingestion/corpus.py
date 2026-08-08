from collections.abc import Iterator
from pathlib import Path

import frontmatter

from .chunker import chunk_document
from .models import Chunk, DocumentMeta

DEFAULT_CORPUS_DIR = Path(__file__).resolve().parents[3] / "corpus"


def iter_corpus_files(corpus_dir: Path = DEFAULT_CORPUS_DIR) -> Iterator[Path]:
    for path in sorted(corpus_dir.rglob("*.md")):
        if path.name == "README.md":
            continue
        yield path


def load_document(path: Path) -> tuple[DocumentMeta, str]:
    post = frontmatter.load(path)
    meta = DocumentMeta(**post.metadata, source_path=str(path))
    return meta, post.content


def list_documents(corpus_dir: Path = DEFAULT_CORPUS_DIR) -> list[DocumentMeta]:
    return [load_document(path)[0] for path in iter_corpus_files(corpus_dir)]


def build_chunks(corpus_dir: Path = DEFAULT_CORPUS_DIR) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in iter_corpus_files(corpus_dir):
        meta, body = load_document(path)
        chunks.extend(chunk_document(meta, body))
    return chunks


def load_chunks_jsonl(path: Path) -> list[Chunk]:
    with path.open(encoding="utf-8") as f:
        return [Chunk.model_validate_json(line) for line in f]

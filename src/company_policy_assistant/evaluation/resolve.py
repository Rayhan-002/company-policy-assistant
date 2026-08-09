import json
from pathlib import Path

from ..ingestion import Chunk
from .models import BenchmarkQuestion, GoldReference

DEFAULT_BENCHMARK_PATH = Path(__file__).resolve().parents[3] / "eval" / "benchmark.json"


def load_benchmark(path: Path = DEFAULT_BENCHMARK_PATH) -> list[BenchmarkQuestion]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [BenchmarkQuestion(**item) for item in data]


def _resolve_reference(reference: GoldReference, chunks: list[Chunk]) -> list[str]:
    return [
        c.chunk_id
        for c in chunks
        if c.document_id == reference.document_id
        and c.version == reference.version
        and c.section_name == reference.section_name
        and c.subsection_name == reference.subsection_name
    ]


def resolve_gold_chunk_ids(question: BenchmarkQuestion, chunks: list[Chunk]) -> list[str]:
    chunk_ids: list[str] = []
    for ref in question.gold_references:
        matches = _resolve_reference(ref, chunks)
        if not matches:
            raise ValueError(
                f"Question {question.id!r}: no chunk matches gold reference "
                f"{ref.document_id} v{ref.version} / {ref.section_name} / {ref.subsection_name}"
            )
        chunk_ids.extend(matches)
    return chunk_ids

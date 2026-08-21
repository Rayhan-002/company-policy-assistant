from ..ingestion.models import Chunk


def prefer_active_version(
    ranked: list[tuple[str, float]], chunk_by_id: dict[str, Chunk]
) -> list[tuple[str, float]]:
    """Drop archived chunks that duplicate an active chunk's section, also present in ranked.

    Rerankers score text relevance, not recency — they have no way to know an archived
    policy version is superseded, so near-identical text across versions (same document,
    same section/subsection) can tie or even outrank the current version's chunk (see
    progress.md 2026-08-09 diagnostic on version-001). This does not touch chunks whose
    section only exists in one version (e.g. "Change Summary from v2.0" is unique text,
    not a duplicate of "Change Summary from v1.0"), so "what changed" style questions are
    unaffected.
    """
    active_keys = {
        (c.document_id, c.section_name, c.subsection_name)
        for chunk_id, _score in ranked
        if (c := chunk_by_id[chunk_id]).status == "active"
    }
    return [
        (chunk_id, score)
        for chunk_id, score in ranked
        if not (
            (c := chunk_by_id[chunk_id]).status == "archived"
            and (c.document_id, c.section_name, c.subsection_name) in active_keys
        )
    ]

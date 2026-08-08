import re
from dataclasses import dataclass

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
_NUMBERED_RE = re.compile(r"^(\d+(?:\.\d+)*)\.?\s+(.*)$")


def _split_number(heading_text: str) -> tuple[str | None, str]:
    m = _NUMBERED_RE.match(heading_text)
    if m:
        return m.group(1), m.group(2).strip()
    return None, heading_text.strip()


@dataclass
class RawNode:
    section_number: str | None
    section_name: str | None
    subsection_number: str | None
    subsection_name: str | None
    text: str


def parse_markdown_body(body: str) -> list[RawNode]:
    """Split a markdown document body into structural nodes.

    Each node is the text found directly under the current H2 (section) /
    H3 (subsection) heading pair at that point in the document — i.e. one
    node per structural unit, not per heading. An H2 with both direct text
    and child H3s produces one node for its direct text plus one node per
    H3 child. Text before the first heading (H1 or otherwise) becomes a
    preamble node with no section/subsection.
    """
    section_number = section_name = None
    subsection_number = subsection_name = None
    buffer: list[str] = []
    nodes: list[RawNode] = []

    def flush() -> None:
        text = "\n".join(buffer).strip()
        buffer.clear()
        if text:
            nodes.append(
                RawNode(section_number, section_name, subsection_number, subsection_name, text)
            )

    for line in body.splitlines():
        m = _HEADING_RE.match(line)
        if not m:
            buffer.append(line)
            continue

        level = len(m.group(1))
        heading_text = m.group(2)

        if level == 1:
            flush()
            section_number = section_name = None
            subsection_number = subsection_name = None
        elif level == 2:
            flush()
            section_number, section_name = _split_number(heading_text)
            subsection_number = subsection_name = None
        elif level == 3:
            flush()
            subsection_number, subsection_name = _split_number(heading_text)
        else:
            # Levels 4+ aren't used as structural boundaries in this corpus.
            buffer.append(line)

    flush()
    return nodes

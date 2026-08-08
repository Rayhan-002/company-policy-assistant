"""Interactive terminal chat with the Company Policy Assistant.

Loads the retrieval pipeline and LLM provider once, then answers as many
questions as you like — showing retrieved/reranked context alongside the
generated answer and citations, so you can see what the RAG is actually
doing at each step, not just the final text.

Usage: uv run python scripts/chat.py
Requires GROQ_API_KEY or GEMINI_API_KEY in .env depending on LLM_PROVIDER (see .env.example).
"""

from dotenv import load_dotenv

load_dotenv()

from company_policy_assistant.generation import answer_question, get_llm_provider  # noqa: E402
from company_policy_assistant.retrieval import Retriever  # noqa: E402


def describe(title: str, version: str, status: str, section: str | None, subsection: str | None) -> str:
    section_label = " / ".join(filter(None, [section, subsection])) or "General"
    return f"{title} v{version} ({status}) - {section_label}"


def print_answer(question: str, retriever: Retriever, llm) -> None:
    answer = answer_question(question, retriever, llm)

    print("\nRetrieved context (after hybrid search + reranking):")
    for r in answer.context_used:
        c = r.chunk
        print(f"  [{r.score:.2f}] {describe(c.title, c.version, c.status, c.section_name, c.subsection_name)}")

    print(f"\nAnswer:\n{answer.text}")

    print("\nSources:")
    for c in answer.citations:
        print(f"  - {describe(c.document_title, c.version, c.status, c.section, c.subsection)}")


def main() -> None:
    print("Loading retrieval pipeline and LLM provider...")
    retriever = Retriever.load()
    try:
        llm = get_llm_provider()
    except KeyError as e:
        print(f"\nMissing environment variable: {e}")
        print("Copy .env.example to .env and fill in an API key (see .env.example for where to get a free one).")
        return
    print(f"Ready (LLM provider: {llm.__class__.__name__}). Type a question, or 'exit' to quit.\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        try:
            print_answer(question, retriever, llm)
        except Exception as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    main()

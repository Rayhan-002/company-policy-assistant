"""Ask the Company Policy Assistant a question end-to-end (retrieval + grounded generation).

Usage: uv run python scripts/ask.py "your question here"
Requires a GROQ_API_KEY or GEMINI_API_KEY in .env (see .env.example) depending on LLM_PROVIDER.
"""

import sys

from dotenv import load_dotenv

load_dotenv()

from company_policy_assistant.generation import answer_question, get_llm_provider  # noqa: E402
from company_policy_assistant.retrieval import Retriever  # noqa: E402

DEFAULT_QUESTION = "I'm a contractor, how many annual leave days do I get?"


def main() -> None:
    question = " ".join(sys.argv[1:]) or DEFAULT_QUESTION
    retriever = Retriever.load()
    try:
        llm = get_llm_provider()
    except KeyError as e:
        print(f"Missing environment variable: {e}")
        print("Copy .env.example to .env and fill in an API key (see .env.example for where to get a free one).")
        return

    answer = answer_question(question, retriever, llm)

    print(f"Q: {question}\n")
    print(answer.text)
    print("\nSources:")
    for c in answer.citations:
        section = " / ".join(filter(None, [c.section, c.subsection])) or "General"
        print(f"  - {c.document_title} v{c.version} ({c.status}) - {section}")


if __name__ == "__main__":
    main()

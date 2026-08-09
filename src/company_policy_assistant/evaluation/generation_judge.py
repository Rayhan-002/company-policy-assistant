import json
import re
from dataclasses import dataclass

from ..generation import LLMProvider, answer_question
from ..retrieval import Retriever
from .models import BenchmarkQuestion

JUDGE_SYSTEM_PROMPT = """You are a strict evaluator for a RAG system's answers. You will be given a question, the context excerpts the system retrieved, the system's generated answer, and a reference answer describing the key facts a correct answer should contain.

Judge two things:
1. "faithful": true if every factual claim in the generated answer is supported by the given context excerpts (no invented facts, no outside knowledge). false otherwise.
2. "correct": true if the generated answer's substance matches the reference answer's key facts (or, if the reference answer says the system should decline due to insufficient information, true only if the generated answer also declines rather than guessing). false otherwise.

Respond with ONLY a JSON object, no other text, in this exact form:
{"faithful": true or false, "correct": true or false, "reasoning": "one brief sentence"}"""

_JSON_RE = re.compile(r"\{.*\}", re.DOTALL)


@dataclass
class QuestionGenerationResult:
    question_id: str
    category: str
    generated_answer: str
    faithful: bool | None
    correct: bool | None
    reasoning: str | None
    error: str | None = None


def _build_judge_prompt(question: str, context: str, generated_answer: str, reference_answer: str) -> str:
    return (
        f"Question: {question}\n\n"
        f"Retrieved context:\n{context}\n\n"
        f"Generated answer:\n{generated_answer}\n\n"
        f"Reference answer (key facts expected):\n{reference_answer}"
    )


def _parse_judge_response(text: str) -> dict:
    match = _JSON_RE.search(text)
    if not match:
        raise ValueError(f"No JSON object found in judge response: {text!r}")
    return json.loads(match.group(0))


def judge_question(
    question: BenchmarkQuestion, retriever: Retriever, llm: LLMProvider
) -> QuestionGenerationResult:
    try:
        answer = answer_question(question.question, retriever, llm)
        context = "\n\n".join(r.chunk.text for r in answer.context_used)
        reference_answer = question.reference_answer or "(no reference answer provided)"

        judge_raw = llm.generate(
            JUDGE_SYSTEM_PROMPT,
            _build_judge_prompt(question.question, context, answer.text, reference_answer),
        )
        parsed = _parse_judge_response(judge_raw)

        return QuestionGenerationResult(
            question_id=question.id,
            category=question.category,
            generated_answer=answer.text,
            faithful=bool(parsed["faithful"]),
            correct=bool(parsed["correct"]),
            reasoning=parsed.get("reasoning"),
        )
    except Exception as e:
        return QuestionGenerationResult(
            question_id=question.id,
            category=question.category,
            generated_answer="",
            faithful=None,
            correct=None,
            reasoning=None,
            error=str(e),
        )


def run_generation_eval(
    questions: list[BenchmarkQuestion], retriever: Retriever, llm: LLMProvider
) -> list[QuestionGenerationResult]:
    results = []
    for i, q in enumerate(questions, start=1):
        print(f"  [{i}/{len(questions)}] {q.id}: {q.question[:60]}...")
        results.append(judge_question(q, retriever, llm))
    return results

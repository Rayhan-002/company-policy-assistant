# Evaluation report — 2026-08-09T08:33:11+00:00

## Retrieval: hybrid-only vs. hybrid + reranked

| Stage | N | Recall@5 | Recall@10 | Precision@5 | MRR | nDCG@5 |
|---|---|---|---|---|---|---|
| Hybrid only | 36 | 55.1% | 73.1% | 15.0% | 48.5% | 46.5% |
| Hybrid + reranked | 36 | 81.0% | 94.9% | 20.6% | 71.7% | 70.9% |

### By category

| Category | N | Hybrid Recall@5 | Reranked Recall@5 | Hybrid MRR | Reranked MRR |
|---|---|---|---|---|---|
| applicability_conflict | 4 | 62.5% | 87.5% | 79.2% | 81.2% |
| broad_coverage | 8 | 62.5% | 100.0% | 65.6% | 93.8% |
| clean_baseline | 6 | 33.3% | 83.3% | 27.1% | 73.2% |
| general_vs_specific | 2 | 16.7% | 83.3% | 25.0% | 100.0% |
| insufficient_evidence | 0 | n/a | n/a | n/a | n/a |
| overlapping_approval | 2 | 75.0% | 75.0% | 37.5% | 33.3% |
| paraphrase_hard | 3 | 0.0% | 33.3% | 0.0% | 22.2% |
| stale_reference | 2 | 100.0% | 100.0% | 66.7% | 41.7% |
| term_disambiguation | 4 | 87.5% | 87.5% | 87.5% | 100.0% |
| version_delta | 5 | 60.0% | 60.0% | 26.4% | 49.9% |

## Generation quality (LLM-judge)

Caveat: the same LLM provider both generates and judges answers here (no separate/stronger judge model configured) — treat this as a directional signal, not an unbiased score.

Judged: 39/39 (errors: 0)
Faithful: 92.3% | Correct: 82.1%

| Category | N | Faithful | Correct |
|---|---|---|---|
| applicability_conflict | 4 | 100.0% | 100.0% |
| broad_coverage | 8 | 100.0% | 75.0% |
| clean_baseline | 6 | 83.3% | 100.0% |
| general_vs_specific | 2 | 100.0% | 50.0% |
| insufficient_evidence | 3 | 100.0% | 100.0% |
| overlapping_approval | 2 | 100.0% | 100.0% |
| paraphrase_hard | 3 | 100.0% | 66.7% |
| stale_reference | 2 | 100.0% | 100.0% |
| term_disambiguation | 4 | 50.0% | 75.0% |
| version_delta | 5 | 100.0% | 60.0% |

### Incorrect answers

- **version-001** (version_delta): The generated answer declines due to insufficient information, but the correct answer can be inferred from the context excerpts, which mention conditions for international remote work.
- **version-002** (version_delta): The generated answer declines due to insufficient information, but the correct answer contains specific key facts not found in the provided context excerpts.
- **term-004** (term_disambiguation): The generated answer lacks the required multi-factor authentication detail and incorrectly implies the Remote Work Policy is relevant to the technical requirements for remote access.
- **general-specific-001** (general_vs_specific): The generated answer does not fully capture the key facts about lodging expenses and incorrectly implies that a single overall maximum can be determined from the provided context.
- **coverage-007** (broad_coverage): The generated answer declines due to insufficient information, but the context excerpts do provide some relevant details about the disclosure process.
- **coverage-008** (broad_coverage): The generated answer introduces unnecessary uncertainty not supported by the context excerpts.
- **paraphrase-001** (paraphrase_hard): The generated answer relies on an archived policy and does not match the key facts in the reference answer.

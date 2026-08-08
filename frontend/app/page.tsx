"use client";

import { useState, type FormEvent } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

interface Citation {
  document_title: string;
  version: string;
  status: string;
  section: string | null;
  subsection: string | null;
}

interface ChatResponse {
  answer: string;
  citations: Citation[];
}

export default function Home() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ChatResponse | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: trimmed }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail ?? `Request failed with status ${res.status}`);
      }

      const data: ChatResponse = await res.json();
      setResult(data);
    } catch (err) {
      const isNetworkError = err instanceof TypeError;
      setError(
        isNetworkError
          ? `Couldn't reach the API at ${API_BASE_URL}. Is the backend running (uv run python scripts/serve.py)?`
          : err instanceof Error
            ? err.message
            : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-1 flex-col items-center bg-zinc-50 px-4 py-12 dark:bg-black">
      <div className="w-full max-w-2xl">
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Nexora Technologies — Policy Assistant
        </h1>
        <p className="mt-1 text-sm text-zinc-500 dark:text-zinc-400">
          Ask about company policies. Answers are grounded in the internal knowledge base only.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3 sm:flex-row">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Can I work remotely from another country?"
            className="flex-1 rounded-lg border border-zinc-300 bg-white px-4 py-2.5 text-sm text-zinc-900 focus:border-zinc-500 focus:outline-none dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-50"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="rounded-lg bg-zinc-900 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-zinc-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-zinc-50 dark:text-zinc-900 dark:hover:bg-zinc-200"
          >
            {loading ? "Asking…" : "Ask"}
          </button>
        </form>

        {error && (
          <div className="mt-6 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-900 dark:bg-red-950 dark:text-red-300">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-8 space-y-6">
            <section>
              <h2 className="text-xs font-semibold tracking-wide text-zinc-500 uppercase dark:text-zinc-400">
                Answer
              </h2>
              <p className="mt-2 text-sm leading-6 whitespace-pre-wrap text-zinc-800 dark:text-zinc-200">
                {result.answer}
              </p>
            </section>

            {result.citations.length > 0 && (
              <section>
                <h2 className="text-xs font-semibold tracking-wide text-zinc-500 uppercase dark:text-zinc-400">
                  Sources
                </h2>
                <ul className="mt-2 space-y-2">
                  {result.citations.map((c, i) => (
                    <li
                      key={i}
                      className="rounded-lg border border-zinc-200 px-3 py-2 text-sm text-zinc-700 dark:border-zinc-800 dark:text-zinc-300"
                    >
                      <span className="font-medium">{c.document_title}</span>{" "}
                      <span className="text-zinc-500 dark:text-zinc-500">
                        v{c.version} ({c.status})
                      </span>
                      {(c.section || c.subsection) && (
                        <span className="text-zinc-500 dark:text-zinc-500">
                          {" "}
                          — {[c.section, c.subsection].filter(Boolean).join(" / ")}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

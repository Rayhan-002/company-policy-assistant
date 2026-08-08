# Nexora Technologies — Policy Corpus (Design Manifest)

This corpus is **deliberately designed to stress retrieval**, not just to exist. Every document below was written to create a specific, named challenge. Keep this manifest in sync as the corpus grows — it's the answer key for building the evaluation benchmark (`plan.md` step 10).

Format: markdown with YAML frontmatter (`document_id`, `title`, `version`, `status`, `effective_from`, `category`, `supersedes`/`superseded_by` where relevant). Will be rendered to PDF later once ingestion needs to prove itself against real PDFs (see `plan.md`).

## Deliberate retrieval challenges

1. **Applicability conflict — leave eligibility.** `leave-policy` (v3, current) grants 20 annual leave days to full-time employees. `contractor-policy` explicitly excludes contractors from that same benefit. A query like *"I'm a contractor, how many leave days do I get?"* must retrieve **both** and correctly resolve the conflict — this is the idea doc's own worked example (§4).

2. **Version delta — remote work.** `remote-work-policy` exists in three versions with a real, meaningful change each time:
   - v1 (archived, 2024-01-01): no international remote work at all.
   - v2 (archived, 2025-03-01): international remote work allowed, ≤30 days/year, manager approval only.
   - v3 (active, 2026-07-01): international remote work allowed, ≤90 days/year, requires manager + HR + Legal approval and a Cross-Border Work Notification.
   Tests both "what's the current rule" (must prefer v3) and "what changed" comparison queries.

3. **Stale cross-reference — handbook drift.** `employee-handbook` was last updated while `leave-policy` v2 (18 days) was active and still states "18 days," while the current `leave-policy` v3 says 20 days. This models the idea doc's core problem statement (§2: "know whether the document you're reading is still current") — the assistant must prefer the specific, current policy over the stale handbook summary, not average or blend them.

4. **Same-word, different-meaning — "leave."** `leave-policy` uses "leave" to mean annual/vacation leave. `attendance-policy` uses "leave" to mean sick/medical absence, with its own separate rules. A query about "sick leave" must not retrieve `leave-policy`'s annual-leave rules, and vice versa.

5. **Same-word, different-meaning — "remote."** `remote-work-policy` uses "remote" to mean work location (where an employee physically works). `acceptable-use-policy` uses "remote access" to mean VPN access into internal systems — an IT/security concept, unrelated to work location. `attendance-policy` also references remote attendance tracking. A query about "working remotely" must not surface the VPN policy, and a query about "remote access to systems" must not surface the work-location policy.

6. **Overlapping approval chains — laptop purchase.** `procurement-policy` sets the dollar-threshold approval chain (department head above $1,000, Finance above $5,000). `device-policy` sets who's eligible for a laptop and what happens on replacement/upgrade, and explicitly defers to `procurement-policy` for the approval threshold. The idea doc's own example question — *"What approval is required for a laptop purchase?"* — genuinely requires both documents to answer correctly; neither alone is sufficient.

7. **General vs. specific — reimbursement.** `expense-policy` sets general reimbursement rules (30-day submission window, 10-business-day payout) and explicitly states travel expenses are governed by `travel-policy` instead, which sets its own specific dollar caps. A query about "maximum travel reimbursement" must retrieve `travel-policy`'s specific caps, not `expense-policy`'s general rule — tests that hybrid/rerank correctly prefers the specific document over the more generic one that also matches on "reimbursement."

8. **Reinforced applicability pattern.** `benefits-policy` also excludes contractors (like `leave-policy` does), cross-referencing `contractor-policy`. This tests whether the system generalizes the "contractors are excluded from X unless stated" pattern correctly rather than needing it re-taught per policy, and doesn't falsely conflate the two distinct benefits being excluded (health insurance vs. annual leave).

9. **Clean control case.** `password-policy` has no deliberate overlaps or ambiguity — a straightforward single-document lookup. Included as a baseline: if retrieval fails on this one, the problem is in the pipeline, not the corpus design.

## Documents

| document_id | category | versions | status |
|---|---|---|---|
| employee-handbook | HR | 1 | active (contains stale leave figure — intentional) |
| leave-policy | HR | v2, v3 | v2 archived, v3 active |
| contractor-policy | HR | 1 | active |
| remote-work-policy | HR | v1, v2, v3 | v1/v2 archived, v3 active |
| attendance-policy | HR | 1 | active |
| benefits-policy | HR | 1 | active |
| expense-policy | Finance | 1 | active |
| travel-policy | Finance | 1 | active |
| procurement-policy | Finance | 1 | active |
| device-policy | IT | 1 | active |
| acceptable-use-policy | IT | 1 | active |
| password-policy | IT | 1 | active |
| code-of-conduct | Legal | 1 | active |
| conflict-of-interest-policy | Legal | 1 | active |

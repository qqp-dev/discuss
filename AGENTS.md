# discuss — Repository orientation

`discuss` is the operator's single-trigger, assisted discussion-post pipeline
for the University of Phoenix (UOPX / Blackboard Ultra) student portal. This
Repository is **qq linked**: it follows the qq methodology for agentic
development.

## Methodology

Read and follow the single canonical universal methodology kernel at
[`methodology/KERNEL.md`](https://github.com/hypermemetic-ai/qq/blob/main/methodology/KERNEL.md)
(the live checkout is `$HOME/projects/qq/methodology/KERNEL.md`). This
Repository's shared language is the canonical glossary linked at `CONCEPTS.md`
plus the trusted appendix in `CONCEPTS.local.md`.

## Single source of truth

[`intent.md`](./intent.md) is the project's single source of truth — the
ratified foundations and structure. Nothing here contradicts it; when in
doubt, `intent.md` wins. Read it before any work.

Non-negotiables from `intent.md`:

- **Never auto-submits**: main-post mode fills the reply field and stops;
  peer-reply mode saves drafts for manual paste. No run path locates or
  clicks a submit control.
- **Never stores or types credentials**: the operator logs in by hand; a
  persistent browser profile carries the session.
- **Human review is mandatory**: the editor step is required, and the
  operator alone reviews and posts.
- **Human pace**: the minimum pages the fixed click-path requires, no retry
  storms.

## Repository boundaries

- `intent.md` — single source of truth (operator-ratified).
- `backlog/` — qq Tasks, documents, and decisions, managed through the
  Backlog CLI (symlinked to the operator-local store; do not hand-edit).
- `src/` — the portal adapter and logic; all portal-specific selectors and
  the click-path live in one adapter module.
- `profile/`, `runs/` — operator-local state (gitignored): browser session
  and per-run working dirs and drafts.
- `CONCEPTS.md`, `CONCEPTS.local.md` — shared vocabulary, canonical + local.
- `docs/` — Repository-owned documentation, including the
  [weekly assignment loop](./docs/weekly-assignment.md).

## Weekly assignment loop

Each UOPX week needs one main discussion post and two classmate replies. The
repeatable loop is documented in [`docs/weekly-assignment.md`](./docs/weekly-assignment.md);
the operator-invoked prompt template lives at `.pi/prompts/weekly-assignment.md`.
Claude assists drafting; the operator alone reviews, edits, and posts.

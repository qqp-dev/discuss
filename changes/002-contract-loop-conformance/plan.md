---
name: plan
purpose: Implementation plan
author: design agent
phase: plan
---

# Plan: `contract-loop-conformance`

**Status:** v1
**Date:** 2026-06-02
**Companion to:** `spec.md` and `tasks.md`

**Goal:** Make `discuss` a conforming instance of portable-core's Contract Loop — a single
current-truth `contract.md`, a per-change `contract-impact.md`, an archive log, a
constitution that declares the loop, and a gate-verified retroactive collapse of change 001.

**Architecture:** Docs/methodology only. Author `contract.md` (genesis snapshot of 001's
shipped behavior) + `CHANGELOG.md`; copy the schema docs by value into `method/schemas/`;
amend `constitution.md`; author both change packages' `contract-impact.md`; verify the 001
collapse with the **operator-home** `contract-currency` reviewer. Every mechanical
conformance fact gets a committed structural pytest oracle in `tests/test_contract_conformance.py`;
the one semantic claim (the contract faithfully reflects 001) is adjudicated by the
independent currency reviewer, not a deterministic test. **No `src/` change.**

**Tech Stack:** Markdown (the four loop artifacts); pytest (mechanical structural oracles,
coverage-neutral — they read files, import no `src`); operator-home `lint-contract-impact.sh`
(D1) and `independent-review` → `contract-currency` reviewer (B1/B2); git history + `CHANGELOG.md`
as the archive.

---

## 1. Tech Choices

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Current-truth artifact | A single root `contract.md`, behavior-narrative layout | Schema I1–I3; one readable thing, not a diff pile. |
| `contract.md` structure | Overview → Pipeline stages (navigate → extract → draft-handoff → fill-no-submit) → Safety invariants (P-I..P-IV) → Auth/render handling → Config & run-dir → Adapters → Methodology & Contract-Loop status | Mirrors portable-core's own `contract.md`; the FR list stays in `spec.md`, the contract is its readable projection (not a flat FR dump). |
| Schema adoption | Copy `contract.md` + `contract-impact.md` + `review-verdict.md` into `method/schemas/` | Schema's required mechanism is adoption-by-copy; copying `review-verdict.md` too keeps the cross-references resolvable (the currency reviewer returns that shape). |
| D1 oracle (well-formedness) | Operator-home `lint-contract-impact.sh`, invoked from a pytest | Not vendored (operator-settled Fork A); reuse the canonical lint rather than re-implement it. |
| B1/B2 oracle (currency/honesty) | Operator-home `contract-currency` reviewer via `independent-review` | The methodology's design: currency is enforced by an independent context-starved reviewer, never a deterministic test. |
| Mechanical-fact oracles | Committed pytest structural tests | Fidelity to the project's anti-waivable-oracle discipline (`learnings.md`); coverage-neutral. |
| Archive log | `CHANGELOG.md`, human-readable, seeded 001+002 | The schema's "human-readable change log" archive member; git history remains the lossless half. |

## 2. Architecture Decisions

- **Genesis snapshot = 001's collapse (N=1).** `contract.md`'s day-one content is the
  synthesized current truth of the only shipped change (001). The operator's retroactive
  formal collapse and the schema's forward-only rule coincide because there is exactly one
  prior change; the only added step is running the currency gate on it. Recorded in `spec.md` §5
  so a future reader does not see a schema violation. *(Alternatives considered: forward-only
  snapshot with no gate run — foreclosed by the operator's Fork B choice.)*
- **Gate via operator-home tooling, not vendored.** `lint-contract-impact.sh` and the
  `contract-currency` reviewer run from PATH / `independent-review`, matching `discuss`'s
  existing posture (it vendors no SDD-floor tooling). *(Alternative: full self-contained vendor —
  foreclosed by Fork A.)*
- **Structural pytest oracles for mechanical facts; reviewer for the semantic one.** "File
  exists / declares X / schema present / declaration well-formed" → falsifiable pytest. "Contract
  faithfully reflects 001's behavior" → `[no-oracle]`, adjudicated by the independent reviewer +
  operator (no deterministic test can prove prose fidelity). This keeps the No-oracle ledger to a
  single, honest entry. *(Alternative: carry every mechanical fact as `[no-oracle]` gate-checked —
  rejected; it inflates the No-oracle ledger and violates the project's oracle discipline.)*
- **001's merged diff is the currency CHANGESET.** 001 is merged (`496e8c1`); the reviewer's
  CHANGESET is that merge's first-parent diff range, resolved by the gate task — not a working-tree diff.

## 3. Open Questions Deferred

| ID | Question | Placeholder | Resolved By |
|----|----------|-------------|-------------|
| Q1 | Exact section granularity of `contract.md` (how finely to split pipeline stages) | Use the §1 layout; one section per pipeline stage + one safety-invariants section | T002 (author + currency reviewer confirms no B1 gap) |
| Q2 | How to resolve 001's merged-diff range for the reviewer | `git diff 496e8c1^1..496e8c1` (first-parent of the 001 merge) | T008 |
| Q3 | Robust base for the "no src changed" diff guard | `git merge-base HEAD main` then name-only diff | T009 |

## 4. Risks & Assumptions

### Risks

1. **The currency reviewer BLOCKs the 001 collapse (B1 staleness or B2 mis-declaration).**
   Mitigation: author `contract.md` directly from 001's FR-001..018 / §4.2 EARS so every
   asserted behavior has a home section; author 001's declaration as a non-empty impact list
   matching the diff. Recovery cost: revise `contract.md` / the declaration and re-dispatch the
   reviewer (revise-and-retry in execute, not an escalation) — minutes.
2. **Operator-home tooling absent at build time** (`lint-contract-impact.sh` / `contract-currency`
   not on PATH). Mitigation: documented load-bearing assumption (`spec.md` §5). Recovery: the
   build re-escalates the scope fork (vendor the tooling — the foreclosed Fork A option), never
   silently weakens the gate. Recovery cost: a scope re-decision.
3. **`test_no_src_modules_changed` fragility** (merge-base resolution in CI/local). Mitigation:
   resolve base via `git merge-base HEAD main`; skip cleanly (not fail) if no base is found.
   Recovery cost: low.

### Assumptions

1. Operator-home `lint-contract-impact.sh` and `independent-review`/`contract-currency` are on
   PATH (the same provisioning as the SDD floor).
2. N=1: change 001 is the only prior change; no other history is in scope for collapse.
3. 001's changeset is recoverable as `496e8c1^1..496e8c1`.
4. The structural conformance tests are the change's own acceptance harness (committed test
   code), not vendored tooling — coverage-neutral, asserting on docs.

## 5. Parallelization Strategy

- **T001 (vendor schemas)** and **T002 (author `contract.md`)** are independent → parallel.
- **US2 — T003 (constitution) and T004 (CHANGELOG)** depend on nothing but T001/T002's
  existence for cross-reference accuracy → parallel with each other.
- **US3 — T005/T006 (the two `contract-impact.md` files)** depend on `contract.md` (T002) and
  the vendored schema (T001) to name real sections. **T007 (learnings note)** depends on T005.
  **T008 (currency gate on 001)** depends on T002 + T005 + the diff resolution (Q2) → it is the
  **last** US3 task and the only `[SUBAGENT]` dispatch.
- **Polish — T009 (blast-radius guard + aggregate green)** depends on all prior tasks.

Critical path: T002 → T005 → T008 → T009. Everything else parallelizes around it.

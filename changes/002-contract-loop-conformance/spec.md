---
name: spec
purpose: Feature specification
author: design agent
phase: specify
---

# Spec: `contract-loop-conformance`

**Status:** Draft
**Date:** 2026-06-02
**Author:** design agent

## 0. Reader's Guide

This change makes `discuss` a **conforming instance** of portable-core's **Contract Loop**
(`method/schemas/contract.md`): a single current-truth `contract.md`, every change a delta
that collapses into it at archive, gated by an independent `contract-currency` reviewer
reading a done-time `contract-impact.md`. A cold reader should read §1 (why) then §3 (the
ten functional requirements) — the four loop artifacts and how `discuss` realizes them are
in §3.2. The two binding forks the operator already settled are recorded in §1.4 / §5 and
in `sign-off.md`. **No `src/` or production code changes** — this is a docs/methodology
change package.

## 1. Vision & Goals

### 1.1 The problem

`discuss` is a **minimal portable-core adoption**: it carries the SDD-flow templates but
never vendored the Contract Loop substrate. Concretely, today:

- there is **no `contract.md`** — current truth is scattered across `changes/001-…/spec.md`
  (v0.3), the tasks Review Log, and `learnings.md`, exactly the "reconstruct the present
  from a pile of overlapping diffs" failure mode the Contract Loop inverts;
- change `001-discussion-draft-pipeline` shipped with contract-collapse recorded **`N/A`**
  (`changes/001-…/learnings.md:117-121`), which explicitly flags this debt and says a
  future builder who vendors the loop should collapse 001's criteria into a new `contract.md`;
- `constitution.md` is **silent** on the Contract Loop — no declared adoption, no
  currency gate on the done/G3 panel;
- there is **no human-readable archive log** (`CHANGELOG.md`); git history is the lossless
  archive but nothing renders it for a human.

The system therefore cannot answer "what does `discuss` do, and why?" from one readable
artifact, and a future change cannot be gated for contract currency because there is no
contract to be current with.

### 1.2 The goal

When complete, `discuss` is a conforming instance per the schema's *Conformance &
portability check*: **one** `contract.md` readable as current truth standalone; a
change-package shape that stays separate until archive and carries a `contract-impact.md`
at done; an append-only archive (git history + `CHANGELOG.md` + retired packages); and the
**propose → apply → archive(collapse)** lifecycle with *done* gated on currency by the
independent `contract-currency` reviewer. Change 001 is **retroactively, formally
collapsed** into the genesis `contract.md` and that collapse is **gate-verified** (the
currency reviewer returns PASS).

### 1.3 Success Criteria

See §4. In one line: a single `contract.md` reflects 001's shipped behavior, both change
packages carry well-formed `contract-impact.md` declarations, the constitution declares the
loop, and the `contract-currency` reviewer returns PASS on the 001 collapse.

### 1.4 Non-goals

- **No tooling vendoring** (operator-settled fork). `discuss` does **not** copy
  `lint-contract-impact.sh` or the `contract-currency` reviewer prompt into the repo; the
  gate runs via the **operator-home** tooling on PATH, the same posture `discuss` already
  uses for the entire SDD floor (it vendors no `lint-spec-flow.sh` either). Only the
  schema *docs* are copied (adoption-by-copy is the schema's required mechanism).
- **No back-collapse of history beyond 001.** Adoption is forward-only; 001 is the only
  prior change, so its collapse *is* the genesis snapshot (see §5).
- **No `src/`, test-of-production, or behavior change** to the `discuss` tool itself. The
  only test code added is the conformance change's own structural oracles (§3, US3).
- **No new runtime dependency** on portable-core; the schema is adopted by copy at a point
  in time, never a runtime link.

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — One readable current truth (Priority: P1)

A maintainer (or a future builder) opens `contract.md` at the repo root and reads, in one
artifact, what `discuss` does and why — the pipeline, the safety invariants, the auth/render
handling, config, and the adapter bindings — without reading the archive or the source.

**Why this priority**: This is the MVP slice — the contract is the substrate the whole loop
rests on. With only this, `discuss` already has a single current-truth artifact, the
inversion the Contract Loop exists to provide.

**Independent Test**: `contract.md` exists at root, declares itself the source of truth (not
subordinate to the archive), and the `contract-currency` reviewer finds no behavioral 001
criterion absent from it.

**Acceptance Scenarios**:

1. **Given** a cold reader with only the repo, **When** they open `contract.md`, **Then** it
   reads as current truth standalone and names itself the source of truth.
2. **Given** change 001's EARS criteria, **When** the contract-currency reviewer compares them
   to `contract.md`, **Then** no criterion's behavior is absent (no B1 staleness).

---

### User Story 2 — Future changes are gated for currency (Priority: P2)

The operator runs a future change through the flow; at done, the constitution requires a
`contract-impact.md`, and the G3 panel dispatches the `contract-currency` reviewer so the
change cannot be marked done while `contract.md` is stale with respect to it.

**Why this priority**: Builds on US1 — without the contract there is nothing to gate. This
story makes drift *structurally impossible* going forward, not just fixed once.

**Independent Test**: `constitution.md` declares Contract Loop adoption, names the
`contract-currency` reviewer as a G3 done-gate concern, and requires every change to carry a
`contract-impact.md`; the schema docs are vendored so the convention is self-described.

**Acceptance Scenarios**:

1. **Given** the amended constitution, **When** a reader looks for the done-gate policy,
   **Then** it names the `contract-currency` G3 concern and the per-change `contract-impact.md`
   requirement.
2. **Given** the repo, **When** a reader looks for the model `discuss` conforms to, **Then**
   `method/schemas/contract.md` and `method/schemas/contract-impact.md` are present as copies.

---

### User Story 3 — Change 001 is formally, verifiably collapsed (Priority: P2)

The recorded `N/A` contract-collapse debt on change 001 is closed: 001 carries a well-formed
`contract-impact.md`, its `learnings.md` note points at it, and the collapse is **gate-verified**
by the `contract-currency` reviewer returning PASS.

**Why this priority**: This is the operator's chosen treatment of 001 (retroactive formal
collapse over forward-only-snapshot). It converts an archive footnote into a gated fact.

**Independent Test**: `lint-contract-impact.sh` reports 001's (and 002's) declaration
well-formed; the currency reviewer dispatched on 001's anchor + contract excerpt +
declaration + merged diff returns PASS, recorded as evidence in the change package.

**Acceptance Scenarios**:

1. **Given** 001's merged diff and its `contract-impact.md`, **When** the currency reviewer
   runs, **Then** it returns PASS (contract current per B1, declaration honest per B2).
2. **Given** 001's `learnings.md`, **When** a reader reaches the contract-collapse note,
   **Then** it references the authored `contract-impact.md` rather than recording `N/A`.

---

### Edge Cases

- **Genesis circularity.** `contract.md` is born *from* 001's collapse **and** must describe
  002's own adoption (the methodology section). Both impacts are declared — 002's own
  `contract-impact.md` names the `added` substrate + methodology section — so there is no
  paradox: the contract that 002 creates also documents that 002 created it.
- **Forward-only vs. retroactive.** The schema's adoption rule is forward-only (day-one
  content is a synthesized snapshot, history is not back-collapsed). The operator chose to
  *formally* collapse 001. These reconcile because **N=1**: with exactly one prior change, the
  synthesized snapshot and 001's collapse are the same content; the only addition is running
  the currency gate on it. This is recorded so a future reader does not read a schema violation.
- **Retrieving 001's merged diff.** 001 is already merged (commit `496e8c1`); the currency
  reviewer's CHANGESET input is the merge's diff range, not a working-tree diff. The gate task
  must resolve that range (the first-parent range of the 001 merge) and feed it to the reviewer.
- **I3 authoring guard.** The contract must never declare itself subordinate to the archive.
  This splits into two limbs: the *presence* of an explicit non-subordination declaration (a
  structural sentinel oracle in `test_contract_exists_declares_source_of_truth`), and the
  *absence* of any contradicting statement anywhere (an unprovable absence — carried as a
  distinct `[no-oracle]`, adjudicated by the completeness/currency reviewer + operator).
- **`none`-mis-declaration trap.** 001 changed real behavior, so its declaration MUST be a
  non-empty impact list, never `none (internal-only)` — a `none` here would be a B2 BLOCK.

## 3. Requirements *(mandatory)*

### 3.1 Functional Requirements

- **FR-001**: The repository MUST contain exactly **one** root `contract.md` that reads as
  current truth standalone, names itself the source of truth, and does not declare itself
  subordinate to the archive (schema invariants I1–I3).
- **FR-002**: `contract.md` MUST reflect **every behavioral acceptance criterion of change
  001** (FR-001..018 / the §4.2 EARS set) — no behavior asserted by a 001 criterion may be
  absent (schema B1, the genesis snapshot's currency).
- **FR-003**: The repository MUST vendor the schema **by copy** at `method/schemas/contract.md`
  and `method/schemas/contract-impact.md` (the schema's required adoption mechanism; no
  runtime link to portable-core).
- **FR-004**: `constitution.md` MUST declare Contract Loop adoption, name the
  `contract-currency` reviewer as a **G3** done-gate concern, and require every change to carry
  a `contract-impact.md` at done.
- **FR-005**: The repository MUST contain a human-readable archive log `CHANGELOG.md`, seeded
  with entries for changes **001** and **002**.
- **FR-006**: Change **001** MUST carry a `changes/001-…/contract-impact.md` that is
  well-formed (schema D1) and consistent with its diff (D2) — a non-empty impact list naming
  the `contract.md` sections 001's behavior collapses into (never `none`).
- **FR-007**: Change **002** MUST carry its own `changes/002-…/contract-impact.md` declaring
  its impact (`added`: the contract substrate + the methodology/Contract-Loop-status section).
- **FR-008**: The `contract-currency` reviewer, dispatched on change 001's anchor (its EARS
  criteria) + the relevant `contract.md` excerpt + 001's declaration + 001's merged diff, MUST
  return **PASS**, and that verdict MUST be **recorded as evidence** in the 002 change package.
- **FR-009**: Change 001's `learnings.md` contract-collapse note (the recorded `N/A`) MUST be
  updated to reference the authored `changes/001-…/contract-impact.md`.
- **FR-010**: The change MUST touch **no non-exempt `src/` production module** and add no
  production code — its only code addition is the structural conformance test module — so the
  constitution's coverage thresholds are unaffected.

### 3.2 Key Entities

The four Contract Loop artifacts, and how `discuss` realizes each:

- **Contract** — `contract.md` at repo root. The single current-truth description of the
  `discuss` tool (its `discussion-draft-pipeline` behavior + why). Invariants I1–I4.
- **Change package** — `changes/NNN-slug/` (`spec.md` propose · `plan.md`+`tasks.md` design ·
  `learnings.md`+`contract-impact.md` done-time · the working-tree diff). Invariants C1–C2.
- **Archive** — the git commit history (lossless) + `CHANGELOG.md` (human-readable) + the
  retired `changes/NNN-slug/` packages. Invariants A1–A3.
- **Contract-impact declaration** — `changes/NNN-slug/contract-impact.md` (schema
  `method/schemas/contract-impact.md`). Invariants D1–D2.

## 4. Success Criteria *(mandatory)*

### 4.1 Measurable Outcomes

- **SC-001**: A cold reader can state what `discuss` does and why from `contract.md` alone,
  without opening `src/` or the archive.
- **SC-002**: Both change packages (001, 002) carry a `contract-impact.md` that
  `lint-contract-impact.sh` reports well-formed (zero D1 failures).
- **SC-003**: The `contract-currency` reviewer returns **PASS** on the 001 collapse (zero B1
  staleness, zero B2 mis-declaration), recorded as evidence.
- **SC-004**: `constitution.md` and `CHANGELOG.md` reflect the adoption such that re-running
  the design/done gates on a fresh session finds `discuss` self-shaped — a conforming instance
  with no shim.
- **SC-005**: The change adds zero production code; the existing test suite stays green at the
  constitution's coverage thresholds (line 85 / branch 75).

### 4.2 Acceptance Criteria (EARS)

```ears
The repository SHALL contain exactly one root contract.md that reads as current truth standalone, names itself the source of truth, and includes an explicit declaration that it is not subordinate to the archive. [test: test_contract_exists_declares_source_of_truth]
The constitution.md SHALL declare Contract Loop adoption, name the contract-currency reviewer as a G3 done-gate concern, and require every change to carry a contract-impact.md at done. [test: test_constitution_declares_contract_loop]
The repository SHALL contain method/schemas/contract.md and method/schemas/contract-impact.md vendored by copy. [test: test_contract_schemas_vendored]
The repository SHALL contain a CHANGELOG.md archive log with entries for changes 001 and 002. [test: test_changelog_has_001_and_002]
WHEN lint-contract-impact is run over change 001's contract-impact.md, it SHALL report the declaration well-formed. [test: test_001_contract_impact_wellformed]
WHEN lint-contract-impact is run over change 002's contract-impact.md, it SHALL report the declaration well-formed. [test: test_002_contract_impact_wellformed]
Change 001's contract-impact.md SHALL be a non-empty impact list naming actual contract.md sections, never `none (internal-only)`. [test: test_001_contract_impact_is_nonempty_list]
WHEN the contract-currency reviewer is dispatched on change 001's anchor, contract excerpt, declaration, and merged diff, it SHALL return PASS, and the verdict SHALL be recorded as evidence in the 002 change package. [test: test_001_currency_verdict_recorded_pass]
Change 001's learnings.md SHALL reference the authored contract-impact.md in place of the recorded `N/A` contract-collapse note. [test: test_001_learnings_references_contract_impact]
IF the conformance change modifies any file under src/, THEN the change SHALL be rejected. [test: test_no_src_modules_changed]
The contract.md SHALL faithfully reflect every behavioral acceptance criterion of change 001 (no deterministic test proves prose fidelity; the independent contract-currency reviewer and the operator adjudicate). [no-oracle]
The contract.md SHALL contain no statement anywhere that subordinates it to the archive (I3 negative — the explicit non-subordination declaration is tested structurally above; the *absence* of any contradicting statement cannot be proven by a deterministic test, so the completeness-consistency / contract-currency reviewer and the operator adjudicate). [no-oracle]
```

## 5. Assumptions

- **Operator-home tooling is on PATH.** `lint-contract-impact.sh` and the `independent-review`
  mechanism that dispatches the `contract-currency` reviewer are available from the operator's
  claude-home (the same provisioning that supplies the SDD floor). *If false:* FR-006/FR-008
  oracles cannot run in-repo and the change must vendor the tooling (the foreclosed Q1 option) —
  re-escalate the scope fork rather than silently weaken the gate.
- **N=1 reconciliation.** 001 is the only prior change, so its formal collapse equals the
  forward-only genesis snapshot; no other history is back-collapsed. *If false* (more prior
  changes surface): only 001 is in scope; others stay archive, uncollapsed.
- **001's merged diff is recoverable** as the first-parent range of merge `496e8c1`. *If
  false:* the gate task must reconstruct the 001 changeset another way before the reviewer can run.
- **The structural conformance oracles are committed test code, not vendored tooling.** Adding
  `tests/test_contract_conformance.py` is the change's own acceptance harness (coverage-neutral,
  asserts on docs), consistent with the project's "every criterion has a falsifiable offline
  oracle" discipline — distinct from the foreclosed tooling-vendoring option.

## 6. Dependencies

- **Change 001 (`discussion-draft-pipeline`)** — merged; supplies the current truth the
  genesis `contract.md` snapshots and the anchor the currency reviewer judges 001 against.
- **portable-core `method/schemas/contract.md` + `contract-impact.md`** — the source of the
  copied schema docs (adoption-by-copy, point-in-time).
- **Operator-home `lint-contract-impact.sh` + `independent-review` / `contract-currency`
  reviewer** — the gate tooling (not vendored; see §5).

## 7. Glossary

- **Contract Loop:** portable-core's §1 capability — contract + change-package + archive +
  contract-impact declaration, with the propose→apply→archive(collapse) lifecycle and a
  currency gate. Schema: `method/schemas/contract.md`.
- **Collapse:** the archive-time step that updates exactly the declared `contract.md` sections
  to current truth, leaving the archive intact.
- **Currency gate (B1/B2):** the independent `contract-currency` reviewer — B1 = a behavioral
  criterion asserts a behavior absent from the contract (stale); B2 = the declaration
  contradicts the diff (mis-declared).
- **Genesis snapshot:** the day-one `contract.md` content, synthesized as the current truth of
  the already-shipped system (here, change 001).

## 8. Brainstorm Log

- **Fork A — conformance depth (operator-settled).** *Artifact-level adoption* (author
  `contract.md`/`CHANGELOG.md`, copy schema docs, amend constitution, declare future
  contract-impact; gate via operator-home tooling) **chosen over** *full self-contained vendor*
  (also copy the lint + reviewer + their tests into the repo). Rationale: matches `discuss`'s
  existing minimal-adoption posture (it vendors no SDD-floor tooling either); lightest change
  that still yields a genuinely conforming instance. → §1.4, §5.
- **Fork B — treatment of change 001 (operator-settled).** *Retroactive formal collapse*
  (author 001's declaration and gate-verify it) **chosen over** *forward-only snapshot* (synthesize
  the contract, leave 001 an uncollapsed archive note). Reconciled with the schema's forward-only
  rule by N=1 (snapshot ≡ collapse). → US3, §5.
- **Sub-choice — structural oracles.** Committed `tests/test_contract_conformance.py` structural
  oracles for the mechanical conformance facts, rather than carrying them as `[no-oracle]`
  admissions. Recommended for fidelity to the project's anti-waivable-oracle discipline; recorded
  as a Binding Choice for operator sign-off. → §5, `sign-off.md`.
- **Genesis circularity** surfaced and resolved (the contract documents its own creation; both
  impacts declared). → §2 Edge Cases.

## 9. Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-06-02 | design agent | Initial spec — Contract Loop conformance; forks A/B settled, structural-oracle sub-choice recorded. |

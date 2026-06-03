---
name: tasks
purpose: Executable task breakdown
author: design agent
phase: tasks
---

# Tasks: `contract-loop-conformance`

**Status:** v1
**Date:** 2026-06-02
**Companion to:** `spec.md` and `plan.md`

**Input**: `changes/002-contract-loop-conformance/{spec.md, plan.md}`.

**Prerequisites**: spec.md ✓, plan.md ✓. The `sign-off.md` ledger template was vendored as a
scaffolding prerequisite (commit `733d94f`).

**Organization**: grouped by user story. Every code task ships an explicit `### Tests` block.
This change is **docs/methodology only** — the sole code added is the structural conformance
test module `tests/test_contract_conformance.py`, whose functions read the doc artifacts and
import no `src`. All tasks are therefore `[no-review]` (mechanical, no behavioral judgment on
production code) except the `[SUBAGENT]` currency dispatch (T008). The substantive gate is
**G3** (done), including the standing `contract-currency` reviewer.

## Format

- Task headers: `### T<id> [markers] [depends: …] — description`.
- Markers: `[P]` parallelizable · `[TDD]` RED-GREEN-REFACTOR · `[SUBAGENT]` dispatch a
  context-starved reviewer · `[no-review]` skips the G2 chunk gate · `[US1..]` story ·
  `[SETUP]/[FOUND]/[POLISH]` phase.

## Shared test harness

All structural oracles live in `tests/test_contract_conformance.py`. Its header (authored in
T001's RED step, reused by every later task):

```python
import json
import pathlib
import shutil
import subprocess

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LINT = shutil.which("lint-contract-impact.sh")


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")
```

---

## Phase 1 — Setup

### T001 [SETUP] [TDD] [P] [no-review] — Vendor the Contract Loop schema docs by copy

**Files touched:** Create `method/schemas/contract.md`, `method/schemas/contract-impact.md`,
`method/schemas/review-verdict.md`; create `tests/test_contract_conformance.py`.

**Expected behavior (FR-003):** the repo carries its own copies of the schema it conforms to
(adoption-by-copy; no runtime link to portable-core). `review-verdict.md` is copied too so the
schema cross-references resolve.

- [x] **T001 — RED → GREEN → REFACTOR**
  - RED: create `tests/test_contract_conformance.py` with the shared header above plus:

```python
def test_contract_schemas_vendored():
    for name in ("contract.md", "contract-impact.md"):
        p = ROOT / "method" / "schemas" / name
        assert p.is_file(), f"method/schemas/{name} must be vendored by copy (FR-003)"
```

  Run `pytest tests/test_contract_conformance.py::test_contract_schemas_vendored -v`; expect
  FAIL (files absent).
  - GREEN: copy the three schema docs verbatim from the operator-home portable-core checkout:

```bash
SRC=~/projects/portable-core/method/schemas
mkdir -p method/schemas
cp "$SRC/contract.md" "$SRC/contract-impact.md" "$SRC/review-verdict.md" method/schemas/
```

  Run the test; expect PASS.
  - REFACTOR: none.

### Tests
- **Unit:** `test_contract_schemas_vendored` — falsifiable: deleting either copy reds it.
- **Non-goals:** does not check schema *content* (verbatim copies; drift is out of scope here).

```ears
The repository SHALL contain method/schemas/contract.md and method/schemas/contract-impact.md vendored by copy. [test: test_contract_schemas_vendored]
```

**Acceptance criterion:** both named schema files exist under `method/schemas/`.

---

## Phase 2 — User Story 1 — One readable current truth (Priority: P1) 🎯 MVP

**Goal**: a single root `contract.md` reads as current truth of `discuss` standalone.

**Independent Test**: `contract.md` exists, declares itself the source of truth, and (deep)
the currency reviewer finds no 001 behavior absent (the latter gated at T008/G3).

### T002 [US1] [FOUND] [TDD] — Author the genesis `contract.md`

**Files touched:** Create `contract.md` (repo root); append to `tests/test_contract_conformance.py`.

**Expected behavior (FR-001, FR-002):** one root `contract.md`, behavior-narrative layout,
that **names itself the source of truth**, does **not** declare itself subordinate to the
archive (I1–I3), and whose sections **reflect every behavioral criterion of change 001**
(FR-001..018 / `changes/001-…/spec.md` §4.2 — the B1 currency target).

**Required section outline** (one pipeline stage per subsection; author prose from the named
sources — `changes/001-…/spec.md`, `constitution.md` §6 principles P-I..P-IV):

1. **Overview & purpose** — single-operator local tool; *why* (assist, never ghostwrite-and-submit).
   Opens with the source-of-truth declaration (see GREEN sentinel).
2. **The pipeline** — `trigger → persistent browser → navigate fixed click-path → wait-for-render
   → classify landing → (auth pause post-nav) → select soonest-due → confirm gate → extract
   prompt → draft handoff → fill reply (no submit)`. Cover FR-001/002/003/004/005/006/017/018.
3. **Draft handoff** — hand prompt to an interactive Claude Code session primed via cwd
   `CLAUDE.md`; mandatory GUI-editor block. Cover FR-007/008/009.
4. **Reply fill (no submit)** — runtime field-type detection, fill, **read-back verify**, never
   submit; on mismatch abort + preserve + manual-paste instruction. Cover FR-010/011/012/014.
5. **Safety invariants** — no-submit (P-II), no credentials persisted (P-I), persist response
   before fill (FR-015), human pace / no retry loop (FR-016, P-I). Map to P-I..P-IV.
6. **Auth & render handling** — persistent profile + "trust this device" session persistence
   (FR-008/subsequent-run); pre-render ForgeRock login-shell classification; condition-based
   bounded wait (no pre-render read).
7. **Portal-coupling quarantine** — every selector + click-path in one adapter module (FR-013, P-III).
8. **Config & run-dir management** — config load, run-dir, durable handoff of the final response.
9. **Adapters** — Playwright persistent profile · Claude Code cwd-`CLAUDE.md` priming · GUI
   editor · desktop launcher (the *how* bindings; the *what* is above).
10. **Methodology & Contract-Loop status** — `discuss` conforms to the Contract Loop
    (`method/schemas/contract.md`, adopted by copy); this `contract.md` is the current truth;
    every change carries `contract-impact.md` at done; the `contract-currency` reviewer gates
    G3; coverage policy lives in `constitution.md`.

- [x] **T002 — RED → GREEN → REFACTOR**
  - RED: append to `tests/test_contract_conformance.py`:

```python
def test_contract_exists_declares_source_of_truth():
    contract = ROOT / "contract.md"
    assert contract.is_file(), "root contract.md must exist (I1)"
    text = contract.read_text(encoding="utf-8").lower()
    assert "source of truth" in text, "contract must name itself the source of truth (I3+)"
    # I3 negative limb (presence of the explicit non-subordination declaration):
    assert ("not subordinate to the archive" in text
            or "never subordinate to the archive" in text), \
        "contract must explicitly declare it is not subordinate to the archive (I3-)"
    # I2: reads as current truth — sanity-check the behavior-narrative sections are present.
    for marker in ("pipeline", "safety", "adapter"):
        assert marker in text, f"contract must describe the {marker} surface (I2)"
```

  Run it; expect FAIL (`contract.md` absent).
  - GREEN: author `contract.md` per the outline above. The Overview MUST open with an explicit
    declaration sentence, e.g.: *"This `contract.md` is the single **source of truth** for what
    `discuss` does and why; the implementation is its regenerable projection, and the archive
    (git history + `CHANGELOG.md`) records how it got here — the contract is never subordinate to
    the archive."* Author every section; ensure each 001 FR's asserted behavior appears in a section.
    Run the test; expect PASS.
  - REFACTOR: read once for I3 — no sentence may declare the contract subordinate to the archive.

### Tests
- **Unit:** `test_contract_exists_declares_source_of_truth` — falsifiable: removing the
  declaration or a section marker reds it.
- **Deep (deferred to T008/G3):** "reflects every 001 criterion" (B1) — `[no-oracle]` here;
  judged by the `contract-currency` reviewer.
- **I3 negative (two limbs):** *presence* of the explicit non-subordination declaration is
  tested structurally (the sentinel assertion above, falsifiable); *absence* of any
  contradicting statement anywhere is `[no-oracle]` — the REFACTOR read + the completeness/G3
  reviewer adjudicate (an absence is not deterministically provable).

```ears
The repository SHALL contain exactly one root contract.md that reads as current truth standalone, names itself the source of truth, and includes an explicit declaration that it is not subordinate to the archive. [test: test_contract_exists_declares_source_of_truth]
The contract.md SHALL faithfully reflect every behavioral acceptance criterion of change 001. [no-oracle]
The contract.md SHALL contain no statement anywhere that subordinates it to the archive (I3 negative; absence not deterministically provable). [no-oracle]
```

**Acceptance criterion:** `contract.md` exists, declares source-of-truth, covers the 10
sections; deep currency deferred to T008.

**Checkpoint**: User Story 1 — a single readable current truth exists.

---

## Phase 3 — User Story 2 — Future changes are gated for currency (Priority: P2)

**Goal**: the constitution declares the loop and the schema docs describe it, so every future
change is gated; the archive log is human-readable.

**Independent Test**: `constitution.md` names the `contract-currency` G3 concern + per-change
`contract-impact.md`; `CHANGELOG.md` lists 001 and 002.

### T003 [US2] [TDD] [P] [depends: T001] — Amend the constitution to declare the Contract Loop

**Files touched:** Modify `constitution.md`; append to `tests/test_contract_conformance.py`.

**Expected behavior (FR-004):** a new section declaring adoption, naming the
`contract-currency` reviewer as a **G3** done-gate concern, and requiring every change to carry
a `contract-impact.md` at done.

- [x] **T003 — RED → GREEN → REFACTOR**
  - RED: append:

```python
def test_constitution_declares_contract_loop():
    text = _read("constitution.md").lower()
    assert "contract loop" in text, "constitution must declare Contract Loop adoption"
    assert "contract-currency" in text, "must name the contract-currency G3 reviewer"
    assert "contract-impact.md" in text, "must require a per-change contract-impact.md"
    assert "g3" in text, "must name the G3 done-gate"
```

  Run it; expect FAIL.
  - GREEN: add a section to `constitution.md` (after §6 Project principles), e.g. **"## 7.
    Contract Loop adoption"**, stating: `discuss` adopts the Contract Loop
    (`method/schemas/contract.md`, by copy); the root `contract.md` is the single current truth;
    every change carries `changes/NNN/contract-impact.md` at done (D1, validated by
    `lint-contract-impact.sh` before any reviewer); the `contract-currency` reviewer is a **G3**
    done-gate concern (B1 staleness / B2 mis-declaration) — a change is not *done* while the
    contract is stale; collapse happens at archive/finishing. Run the test; expect PASS.
  - REFACTOR: none.

### Tests
- **Unit:** `test_constitution_declares_contract_loop` — falsifiable: dropping any of the four
  required mentions reds it.

```ears
The constitution.md SHALL declare Contract Loop adoption, name the contract-currency reviewer as a G3 done-gate concern, and require every change to carry a contract-impact.md at done. [test: test_constitution_declares_contract_loop]
```

**Acceptance criterion:** the four required mentions are present in `constitution.md`.

### T004 [US2] [TDD] [P] [depends: T002] — Seed the `CHANGELOG.md` archive log

**Files touched:** Create `CHANGELOG.md` (repo root); append to `tests/test_contract_conformance.py`.

**Expected behavior (FR-005):** a human-readable archive log with entries for 001 and 002.

- [x] **T004 — RED → GREEN → REFACTOR**
  - RED: append:

```python
def test_changelog_has_001_and_002():
    text = _read("CHANGELOG.md")
    assert "001" in text and "discussion-draft-pipeline" in text, "CHANGELOG must record change 001"
    assert "002" in text and "contract-loop-conformance" in text, "CHANGELOG must record change 002"
```

  Run it; expect FAIL.
  - GREEN: create `CHANGELOG.md`, reverse-chronological:
    - **002 — contract-loop-conformance**: adopt the Contract Loop — genesis `contract.md`,
      schema vendoring, constitution amendment, retroactive gate-verified collapse of 001.
    - **001 — discussion-draft-pipeline**: live-verified navigate → extract → draft-handoff →
      fill-no-submit pipeline; shipped after two escalations (render/auth redesign).
    Run the test; expect PASS.
  - REFACTOR: none.

### Tests
- **Unit:** `test_changelog_has_001_and_002` — falsifiable: removing either entry reds it.

```ears
The repository SHALL contain a CHANGELOG.md archive log with entries for changes 001 and 002. [test: test_changelog_has_001_and_002]
```

**Acceptance criterion:** `CHANGELOG.md` lists both changes by id and slug.

**Checkpoint**: User Stories 1 AND 2 both hold independently.

---

## Phase 4 — User Story 3 — Change 001 formally, verifiably collapsed (Priority: P2)

**Goal**: close the recorded `N/A` debt — 001 carries a well-formed declaration, its learnings
note points at it, and the currency reviewer returns PASS on the collapse.

**Independent Test**: `lint-contract-impact.sh` passes on 001 and 002; the currency reviewer
PASSes on 001; 001's learnings reference the declaration.

### T005 [US3] [TDD] [depends: T001, T002] — Author 001's `contract-impact.md`

**Files touched:** Create `changes/001-discussion-draft-pipeline/contract-impact.md`; append to
`tests/test_contract_conformance.py`.

**Expected behavior (FR-006):** a well-formed (D1), non-empty impact **list** (never `none`)
naming the actual `contract.md` sections 001's behavior collapses into, consistent with 001's
diff (D2).

- [x] **T005 — RED → GREEN → REFACTOR**
  - RED: append:

```python
@pytest.mark.skipif(LINT is None, reason="operator-home lint-contract-impact.sh not on PATH")
def test_001_contract_impact_wellformed():
    d = ROOT / "changes" / "001-discussion-draft-pipeline"
    r = subprocess.run([LINT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, (r.stderr or r.stdout)


def test_001_contract_impact_is_nonempty_list():
    text = _read("changes/001-discussion-draft-pipeline/contract-impact.md")
    assert "none (internal-only)" not in text, "001 changed behavior — must not declare none (B2 trap)"
    assert "section:" in text and "kind:" in text, "001 declaration must be a non-empty impact list"
```

  Run both; expect FAIL (declaration absent).
  - GREEN: author `changes/001-discussion-draft-pipeline/contract-impact.md` per
    `method/schemas/contract-impact.md` — `change: 001`, an `impact:` list whose entries name the
    `contract.md` sections (e.g. `The pipeline` / `Reply fill (no submit)` / `Safety invariants` /
    `Auth & render handling` / `Portal-coupling quarantine`), each `kind: added` (genesis), with a
    one-line `note`; a `rationale` tying the impact to 001's diff (the whole tool's behavior, now
    described by the contract for the first time). Run the tests; expect PASS.
  - REFACTOR: confirm every named `section:` is an actual heading in `contract.md`.

### Tests
- **Unit:** `test_001_contract_impact_wellformed` (D1, via the real lint) +
  `test_001_contract_impact_is_nonempty_list` (B2 trap guard). Falsifiable: a `none` declaration
  or a missing field reds them.
- **Skip semantics:** the D1 test skips (not fails) if the operator-home lint is absent — the
  load-bearing assumption (`spec.md` §5); on a provisioned host it runs.

```ears
WHEN lint-contract-impact is run over change 001's contract-impact.md, it SHALL report the declaration well-formed. [test: test_001_contract_impact_wellformed]
Change 001's contract-impact.md SHALL be a non-empty impact list naming actual contract.md sections, never `none (internal-only)`. [test: test_001_contract_impact_is_nonempty_list]
```

**Acceptance criterion:** 001's declaration is present, well-formed, a non-empty list of real sections.

### T006 [US3] [TDD] [depends: T001, T002] — Author 002's own `contract-impact.md`

**Files touched:** Create `changes/002-contract-loop-conformance/contract-impact.md`; append to
the test module.

**Expected behavior (FR-007):** this change's own declaration — `added`: the contract substrate
+ the Methodology/Contract-Loop-status section it introduces.

- [x] **T006 — RED → GREEN → REFACTOR**
  - RED: append:

```python
@pytest.mark.skipif(LINT is None, reason="operator-home lint-contract-impact.sh not on PATH")
def test_002_contract_impact_wellformed():
    d = ROOT / "changes" / "002-contract-loop-conformance"
    r = subprocess.run([LINT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, (r.stderr or r.stdout)
```

  Run it; expect FAIL.
  - GREEN: author `changes/002-contract-loop-conformance/contract-impact.md` — `change: 002`,
    `impact:` list with at least `{section: "Methodology & Contract-Loop status", kind: added,
    note: …}` (and the genesis of the contract itself), `rationale` tying it to this change's diff.
    Run the test; expect PASS.
  - REFACTOR: none.

### Tests
- **Unit:** `test_002_contract_impact_wellformed` (D1, via the real lint; skips if absent).

```ears
WHEN lint-contract-impact is run over change 002's contract-impact.md, it SHALL report the declaration well-formed. [test: test_002_contract_impact_wellformed]
```

**Acceptance criterion:** 002's declaration is present and well-formed.

### T007 [US3] [TDD] [depends: T005] — Close the recorded `N/A` debt in 001's learnings

**Files touched:** Modify `changes/001-discussion-draft-pipeline/learnings.md` (the
"Contract-collapse recorded N/A" bullet, lines ~117-121); append to the test module.

**Expected behavior (FR-009):** the note references the now-authored declaration instead of
recording `N/A`.

- [ ] **T007 — RED → GREEN → REFACTOR**
  - RED: append:

```python
def test_001_learnings_references_contract_impact():
    text = _read("changes/001-discussion-draft-pipeline/learnings.md")
    assert "contract-impact.md" in text, "001 learnings must reference the authored declaration"
```

  Run it; expect FAIL (the current note says the substrate is not vendored / N/A).
  - GREEN: update the bullet to note that change 002 vendored the Contract Loop and 001 was
    retroactively collapsed — see `changes/001-discussion-draft-pipeline/contract-impact.md`.
    Keep the historical context; add the forward reference. Run the test; expect PASS.
  - REFACTOR: none.

### Tests
- **Unit:** `test_001_learnings_references_contract_impact` — falsifiable: without the reference it reds.

```ears
Change 001's learnings.md SHALL reference the authored contract-impact.md in place of the recorded `N/A` contract-collapse note. [test: test_001_learnings_references_contract_impact]
```

**Acceptance criterion:** 001's learnings.md references `contract-impact.md`.

### T008 [US3] [SUBAGENT] [depends: T002, T005] — Gate-verify the 001 collapse with the currency reviewer

**Files touched:** Create `changes/002-contract-loop-conformance/evidence-001-currency-verdict.json`;
append to the test module.

**Expected behavior (FR-008):** dispatch the **operator-home** `contract-currency` reviewer
(`~/projects/portable-core/method/skills/independent-review/reviewers/contract-currency.md`) as a
context-starved subagent, substituting its four placeholders, and record the returned
`review-verdict` JSON. The verdict MUST be **PASS**.

**The four inputs (the reviewer's only context — withhold all builder narrative):**
- **ANCHOR** = change 001's §4.2 EARS criteria (from `changes/001-discussion-draft-pipeline/spec.md`).
- **CONTRACT_EXCERPT** = the relevant `contract.md` sections (pipeline, reply-fill, safety,
  auth/render, quarantine).
- **CONTRACT_IMPACT** = `changes/001-discussion-draft-pipeline/contract-impact.md`.
- **CHANGESET** = 001's merged diff: `git diff 496e8c1^1..496e8c1` (Q2). If that range does not
  resolve to 001's content, reconstruct the 001 changeset before dispatching.

- [ ] **T008 — dispatch + record**
  - Resolve the CHANGESET (Q2). Dispatch the reviewer subagent with the four inputs.
  - Write the returned JSON object to `evidence-001-currency-verdict.json`.
  - RED→GREEN test (append):

```python
def test_001_currency_verdict_recorded_pass():
    p = ROOT / "changes" / "002-contract-loop-conformance" / "evidence-001-currency-verdict.json"
    assert p.is_file(), "currency verdict evidence must be recorded (FR-008)"
    verdict = json.loads(p.read_text(encoding="utf-8"))
    assert verdict.get("verdict") == "PASS", f"currency reviewer must PASS on the 001 collapse, got {verdict.get('verdict')}"
```

  - **If the reviewer returns BLOCK** (B1: a 001 behavior absent from `contract.md`; B2: the
    declaration contradicts the diff): this is a **revise-and-retry in execute** — fix
    `contract.md` (T002) or 001's declaration (T005) and re-dispatch; do **not** force PASS or
    edit the evidence by hand. A bounce past the cap promotes to escalation.

### Tests
- **Recorded-gate oracle:** `test_001_currency_verdict_recorded_pass` — asserts the independent
  reviewer's verdict was recorded as PASS. The *authority* is the reviewer (and 002's own G3
  currency run), not this test; the test guards that the gate was run and passed.

```ears
WHEN the contract-currency reviewer is dispatched on change 001's anchor, contract excerpt, declaration, and merged diff, it SHALL return PASS, and the verdict SHALL be recorded as evidence in the 002 change package. [test: test_001_currency_verdict_recorded_pass]
```

**Acceptance criterion:** `evidence-001-currency-verdict.json` records `verdict: PASS`.

**Checkpoint**: User Story 3 — 001 is formally collapsed and gate-verified.

---

## Phase 5 — Polish & cross-cutting

### T009 [POLISH] [TDD] [no-review] [depends: T001..T008] — Blast-radius guard + aggregate green

**Files touched:** Append to `tests/test_contract_conformance.py`.

**Expected behavior (FR-010):** prove the change touched no `src/` production module; the full
suite stays green at the constitution's coverage thresholds (line 85 / branch 75).

- [ ] **T009 — RED → GREEN → REFACTOR**
  - RED: append:

```python
def test_no_src_modules_changed():
    # FR-010 — docs/methodology-only blast radius: no file under src/ changed vs the branch base.
    base = subprocess.run(["git", "merge-base", "HEAD", "main"],
                          cwd=ROOT, capture_output=True, text=True)
    if base.returncode != 0 or not base.stdout.strip():
        pytest.skip("no merge-base with main resolvable")
    diff = subprocess.run(["git", "diff", "--name-only", base.stdout.strip(), "HEAD"],
                          cwd=ROOT, capture_output=True, text=True)
    changed = [f for f in diff.stdout.splitlines() if f.startswith("src/")]
    assert changed == [], f"conformance change must touch no src/ module, found: {changed}"
```

  Run it; expect PASS already (no `src/` touched) — this is a *guard*, green from the start, that
  reds only if a future edit strays into `src/`.
  - GREEN: n/a (guard).
  - REFACTOR: none.
  - Run the **full suite**: `pytest -q` and confirm coverage stays ≥ thresholds.

### Tests
- **Guard:** `test_no_src_modules_changed` — reds iff any `src/` file is modified on the branch.
- **Aggregate:** `pytest -q` green; coverage unchanged (no new production code).

```ears
IF the conformance change modifies any file under src/, THEN the change SHALL be rejected. [test: test_no_src_modules_changed]
```

**Acceptance criterion:** the suite is green; no `src/` path appears in the branch diff.

---

## Dependencies & execution order

- **T001 (schemas)** ∥ **T002 (contract.md)** — independent; start both.
- **T003 (constitution)** ∥ **T004 (CHANGELOG)** — after T001/T002 exist (for accurate cross-refs).
- **T005, T006 (declarations)** — after T001 + T002 (must name real sections).
- **T007 (learnings)** — after T005.
- **T008 (currency gate)** — after T002 + T005; the only `[SUBAGENT]` task; last substantive step.
- **T009 (guard + aggregate)** — after all.

Critical path: T002 → T005 → T008 → T009. Commit after each task whose tests pass. One checkbox
per task is the resumable handoff state.

## Review Log

> Append-only. Execute appends one row per gate verdict (G2/G3) as it runs. Empty until execution begins.

| Gate | Anchor | Verdict | Key findings |
|------|--------|---------|--------------|
| G1 (design exit) | spec+plan+tasks+sign-off | clear (after 1 bounce) | testability BLOCK→PASS: FR-001/I3 was a multi-limb criterion whose I3-negative limb was unasserted; split into a structural non-subordination sentinel + a distinct `[no-oracle]`. completeness/scope/sign-off-faithfulness PASS. No-oracle residue (2: B1 prose-fidelity, I3-negative absence) routed to operator via sign-off § No-oracle Admissions. |
| G2 (T001) | test_contract_schemas_vendored | n/a — skipped | `[no-review]` task; touches only exempt schema globs (`method/schemas/**`) + the conformance test module. No production code for a panel to judge. |
| G2 (T002) | test_contract_exists_declares_source_of_truth | n/a — skipped | `[no-review]` per the tasks preamble (docs/methodology only). The contract's 001-fidelity (B1) is the deferred deep judgment, gated at T008 + the G3 `contract-currency`/`spec-match` panel — no production code for a G2 panel. |
| G2 (T003) | test_constitution_declares_contract_loop | n/a — skipped | `[no-review]` docs task (constitution.md amendment); no `src/` production code. |
| G2 (T004) | test_changelog_has_001_and_002 | n/a — skipped | `[no-review]` docs task (new CHANGELOG.md); no `src/` production code. |
| G2 (T005) | test_001_contract_impact_wellformed + ..._is_nonempty_list | n/a — skipped | `[no-review]` docs task (001's contract-impact.md declaration). D1 well-formedness verified by the real `lint-contract-impact.sh`; B1/B2 semantic judgment is T008's currency gate. No `src/` production code. |
| G2 (T006) | test_002_contract_impact_wellformed | n/a — skipped | `[no-review]` docs task (002's own contract-impact.md). D1 verified by the real lint; B1/B2 deferred to the G3 `contract-currency` reviewer. No `src/` production code. |

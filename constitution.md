# Constitution: `discuss`

**Project:** `discuss`
**Status:** v1
**Last updated:** 2026-06-01

This constitution declares project policy. Discipline-gate skills read it; the planner negotiates changes here, never inline in tasks.

`discuss` is a single-operator local tool: on one trigger it drives a logged-in
UOPX student-portal session (Playwright, persistent profile) to the discussion with
the soonest upcoming due date, extracts the plaintext prompt, hands it to an
interactive Claude Code session that helps the operator reason through the topic and
draft a response, opens that draft in a GUI editor for final edits, and fills the
result into the reply form — **without submitting it**. The operator reviews and posts.

---

## 1. Testing policy

```yaml
coverage_threshold:
  line: 85
  branch: 75

coverage_exemptions:
  - path: "src/discuss/browser.py"
    reason: "Playwright persistent-session lifecycle + login detection. Honestly exercisable only against the live, login-gated UOPX portal, which the Respectful-guest principle forbids us from automating or hammering in CI. Verified by the operator-run live checklist (see §6), not unit tests."
  - path: "src/discuss/portal_adapter.py"
    reason: "Live navigate/extract/fill against the real portal DOM — same live-only, must-not-hammer justification as browser.py. All PURE parsing/selection logic (due-date → target choice, prompt-text extraction from an HTML string) lives in src/discuss/portal_parse.py, which is NOT exempt and is covered by saved-HTML fixtures."
  - path: "launcher/**"
    reason: "Desktop launcher entry (.desktop) and shell shim — non-code artifacts, smoke-checked manually."
  - path: "templates/**"
    reason: "The primed workflow CLAUDE.md is a prompt artifact, not code; judged by behavior in a live run, not coverage."

mutation_testing: false
```

**Justification for defaults.** Thresholds apply to all non-exempt code. The exemptions
above quarantine exactly the surface that touches a live, login-gated, third-party portal
we are ethically bound not to automate aggressively; everything pure and portal-agnostic
(parsing, target selection, the file-handoff orchestration, run-dir management) stays
fully covered.

---

## 2. Testing principles

```yaml
testing_principles:
  - per-test-comment-required
  - no-mock-the-system-under-test
  - prefer-controlled-real-boundaries
```

**How these bind this project.** `no-mock-the-system-under-test`: parsing tests run
against **saved real HTML** captured from the live portal, never a hand-stubbed DOM that
pretends to be UOPX. `prefer-controlled-real-boundaries`: saved-HTML fixtures are the
controlled real boundary for parsing logic; the live portal is the real boundary for
navigate/extract/fill, exercised through the operator verification checklist — a fixture
is honestly a proxy for *parsing only* and is never treated as proof that live injection
works.

---

## 3. Memory policy

Memory is intentionally out of scope. The constitution carries no memory configuration.

---

## 4. Learning-discipline policy

```yaml
learning_discipline:
  min_section_words: 15
  weasel_words:
    - "be more careful"
    - "in general"
    - "as always"
    - "as expected"
    - "no surprises"
    - "smooth sailing"
    - "all went well"
  enforce_builder_perspective_informs_lesson: true
```

---

## 5. Justifications log

(Empty. Append entries here when loosening any of the above thresholds, with date and rationale.)

---

## 6. Project principles

These are governance-level invariants. Any change whose artifacts violate one of these
should not pass a review gate.

- **P-I — Respectful guest.** The tool reuses the operator's own live, human-authenticated
  session; it never stores credentials, never scrapes or crawls beyond the single fixed
  click-path, runs at human pace (no tight polling/retry loops), and on failure stops and
  reports rather than hammering the server. A run touches the minimum number of pages.

- **P-II — Human-in-the-loop.** The operator reasons (the session draws out their stance
  and evidence), edits (the GUI editor step is mandatory, never skipped), and posts (the
  tool **fills** the reply form and stops — it never auto-submits). The tool assists the
  operator's own work; it does not ghostwrite-and-submit.

- **P-III — Portal-coupling quarantine.** Every UOPX-specific selector and the click-path
  live in one adapter module. A portal markup change is a one-file fix. The reply-field
  type (plain textarea vs rich-text/contenteditable) is **detected at runtime**, never
  hard-coded.

- **P-IV — Observed effect, not reported success.** A browser action is verified by
  reading the resulting state back (e.g. the reply field's rendered content equals the
  intended text), never by trusting that the call returned without error. `fill()`
  returning is not proof the text landed.

---

## 7. Contract Loop adoption

`discuss` adopts portable-core's **Contract Loop** (`method/schemas/contract.md`), vendored
**by copy** into `method/schemas/` — there is no runtime link to portable-core. The model has
four artifacts and one lifecycle:

- **The contract is the single current truth.** The root `contract.md` is the source of truth
  for what `discuss` does and why; the implementation under `src/` is its regenerable
  projection. There is exactly one contract, readable standalone, never subordinate to the
  archive.
- **Every change carries a `contract-impact.md` at done.** Each change package
  (`changes/NNN-slug/`) stays physically separate from the contract until archive and MUST
  carry a `changes/NNN-slug/contract-impact.md` (schema `method/schemas/contract-impact.md`)
  declaring how it touches the contract. This is validated deterministically by
  `lint-contract-impact.sh` (the floor) before any reviewer is dispatched.
- **Collapse at archive.** At finishing, the change's delta is collapsed into **exactly the
  declared** `contract.md` sections, updating them to current truth, while leaving the archive
  (git history + `CHANGELOG.md` + the retired package) intact.
- **Currency is a G3 done-gate concern.** The independent `contract-currency` reviewer is a
  concern on the **G3** completion panel: it BLOCKs a **stale** contract (a behavioral
  acceptance criterion asserts a behavior absent from the contract — B1) or a **mis-declared**
  impact (the declaration contradicts the diff — B2). A change is **not done** while the
  contract is stale with respect to it; the collapse that clears it happens at archive /
  finishing, never on the builder's say-so.

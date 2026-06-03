---
loop: [gate]
kind: substrate
name: review-verdict
purpose: The structured object every independent reviewer subagent returns; the unit the independent-review mechanism aggregates and that compounding harvests.
author: reviewer subagent (one per concern), produced under the independent-review skill
phase: design (G1) / execute (G2, G3) — the review gates
---

# Review Verdict

Each independent reviewer subagent — dispatched with only `(changeset, anchor, one
concern)` — returns exactly one **review verdict**: its judgment of the changeset
against the anchor for its single concern. The `independent-review` mechanism
collects one verdict per concern and aggregates them deterministically (FR-002,
FR-003). A verdict is data, not prose: it is a JSON object that MAY be embedded in a
reply and is **extracted** by the mechanism (reviewers sometimes wrap it in prose —
see Notes).

## Schema

A review verdict has 2 top-level fields:

1. **verdict** — the reviewer's roll-up for its concern. One of:
   - `PASS` — no in-scope anchor element was found violated.
   - `BLOCK` — at least one in-scope anchor element was found violated.

   A `no-oracle` finding does **not** by itself make a reviewer `BLOCK`; the verdict
   is `PASS` unless something is actually `violated`. (Residue is decided at the panel
   level, not by the individual reviewer — see Aggregation.)

2. **findings** — a non-empty list, **one entry per in-scope anchor element** the
   reviewer was asked to judge (never bundled, never omitted). Each finding has 3
   fields:

   - **anchor_ref** — a stable id of the anchor element judged. An EARS criterion id
     (e.g. `EARS-2`), a named invariant (`INV-1`), a constitution clause
     (`constitution §1`), or a `local-opinions` entry id. MUST reference an element
     actually present in the anchor the reviewer was handed — never the builder's
     account, never an invented criterion.
   - **status** — one of:
     - `satisfied` — confirmed to hold against the changeset.
     - `violated` — confirmed **not** to hold; `evidence` cites the concrete failure.
     - `no-oracle` — cannot be adjudicated (no test exists, the criterion is marked
       `[no-oracle]`, it is inherently subjective, or there is genuine reviewer
       uncertainty with no ground truth). **Neither a pass nor a fail** — the reviewer
       MUST NOT manufacture one.
   - **evidence** — a concrete one-sentence justification anchored to the changeset
     and the anchor element (what in the diff makes this satisfied/violated, or why
     no oracle exists). Never references who wrote the change or why.

## Aggregation (panel level — FR-003)

The `independent-review` mechanism aggregates the panel's verdicts into one of three
outcomes. The rules are deterministic given the verdicts:

- **clear** — every reviewer's `verdict` is `PASS` **and** no finding anywhere in the
  panel has status `no-oracle`.
- **bounce** — at least one reviewer's `verdict` is `BLOCK` (i.e. some finding is
  `violated`). Routes to the responsible role for fix-and-retry (G1 → design;
  G2/G3 → execute), re-reviewing only the affected concerns where possible (FR-014,
  FR-017).
- **human-residue** — at least one finding (anywhere in the panel) has status
  `no-oracle` on an in-scope criterion. Surfaced to a human as a distinct outcome
  (FR-015) — never silently passed, never silently failed.

`bounce` and `human-residue` can co-occur (a panel may both find a violation **and**
leave a no-oracle criterion). Both are surfaced; neither masks the other.

## Template

```json
{
  "verdict": "PASS | BLOCK",
  "findings": [
    {"anchor_ref": "<criterion id | invariant name | clause>", "status": "satisfied | violated | no-oracle", "evidence": "<one sentence, anchored to the change>"}
  ]
}
```

## Examples

These are the actual verdicts the T002 spike reviewers returned
(`tooling/tests/probes/probe-review-dispatch.md`); they validate against this schema by
construction.

**A — BLOCK with findings** (the `spec-match` reviewer; the change fails EARS-2):

```json
{
  "verdict": "BLOCK",
  "findings": [
    {"anchor_ref": "EARS-1", "status": "satisfied", "evidence": "For n=0 the guard n<1 is true, so the function returns False as required."},
    {"anchor_ref": "EARS-2", "status": "violated", "evidence": "For values greater than 65535 the function falls through to return True, but the criterion requires False."},
    {"anchor_ref": "EARS-3", "status": "no-oracle", "evidence": "Name suitability is marked [no-oracle] and cannot be automatically adjudicated from the diff."}
  ]
}
```

**B — PASS** (the `invariants` reviewer; the invariant holds):

```json
{
  "verdict": "PASS",
  "findings": [
    {"anchor_ref": "INV-1", "status": "satisfied", "evidence": "is_valid_port returns False for n<1 and True otherwise, always a boolean with no None return or raise for any integer input."}
  ]
}
```

**C — PASS verdict carrying a no-oracle finding** (illustrative; a reviewer whose only
in-scope element has no oracle). Note the verdict is `PASS` (nothing was *violated*),
yet the panel routes this to **human-residue** because of the `no-oracle` finding —
showing why residue is an aggregation outcome, not a reviewer verdict:

```json
{
  "verdict": "PASS",
  "findings": [
    {"anchor_ref": "EARS-3", "status": "no-oracle", "evidence": "Criterion is marked [no-oracle]; no test exists, so satisfaction cannot be adjudicated from the change."}
  ]
}
```

## Compounding (FR-021)

Findings are the harvest unit. They are recorded in the change record (per T019) and,
at compaction/triage, `learnings-completeness-check` consumes them: a recurring
preference-shaped finding is promotable to a scoped, advisory `local-opinions.md`
entry (see `method/schemas/local-opinions.md`); a hard-line finding is promotable to a
`constitution.md` amendment under the existing §5 justification discipline.
The flat `anchor_ref` + `status` + `evidence` shape is what makes a finding
harvestable without a governance engine.

## Notes / constraints

- **Extraction, not assumption.** A reviewer's reply MAY contain prose before or after
  the JSON object (observed in T002). The mechanism extracts the first complete JSON
  object and validates it against this schema; reviewers SHOULD return only the object,
  but the mechanism does not depend on it.
- **One finding per in-scope element**, never bundled and never omitted. An empty
  `findings` list is invalid — a reviewer that judged nothing has no verdict to give.
- **`anchor_ref` must resolve** to an element in the handed anchor. A finding against
  an element not in the anchor is a malformed verdict (the reviewer hallucinated scope).
- **Independence is in the input, recorded in the output.** The verdict never cites the
  builder; if it does, the dispatch was not context-starved (SC-001 violation).

---
name: learnings
feature: 002-contract-loop-conformance
author: execute agent
phase: compaction
---

# Learnings: `contract-loop-conformance`

A docs/methodology-only change that made `discuss` a conforming instance of the Contract
Loop: a genesis `contract.md`, vendored schema docs, a constitution amendment, both change
packages' `contract-impact.md`, and a gate-verified retroactive collapse of change 001. It
ran clean through G3 with no escalations — but several judgment calls were load-bearing and
a future builder should not have to re-derive them.

## Notable Challenges Overcome

- **Challenge:** The genesis circularity — `contract.md` is born *from* 001's collapse yet
  must also document 002's own adoption, and 002's diff textually *creates the entire file*
  (all 10 sections). A naive 002 declaration would list every section as `added`, which the
  currency reviewer would flag as B2 mis-declaration (the diff also "added" the pipeline
  sections, but those are 001's behavior).
  **How:** split the impact by *what each change made true*, not by *what each diff textually
  wrote*. 001's `contract-impact.md` declares the eight behavioral sections (pipeline, draft
  handoff, reply-fill, safety, auth/render, quarantine, config, adapters); 002's declares only
  the two framing sections it actually established (Overview's source-of-truth declaration +
  the Methodology & Contract-Loop status section). Both reviewers (T008 on 001, G3 on 002)
  returned PASS with no B2.
  **Generalizes:** a contract-impact declaration names the sections describing the behavior
  *this change* made true — never every section its diff happens to touch. When one change
  authors a file that snapshots a *prior* change's behavior, that behavior belongs to the
  prior change's declaration; the authoring change declares only its own delta.

- **Challenge:** Dispatching the `contract-currency` reviewer on 001's *merged* collapse
  required feeding it 001's changeset, which is 20.8k lines / 2.25 MB — almost entirely
  captured HTML portal fixtures (reply_form.html alone is 5.5k lines), not behavior.
  **How:** wrote the changeset to a controlled evidence file the subagent reads as its sole
  CHANGESET input, with the three small inputs (anchor, contract excerpt, declaration) inline,
  and a neutral note that the bulk is captured fixtures while the behavior-defining changes
  live under `src/`/`tests/`/`templates/`. Kept it context-starved by forbidding reading any
  other repo file. After the gate cleared, removed the 2.25 MB patch (deterministically
  regenerable via `git diff 496e8c1^1..496e8c1`) and kept only the verdict JSON as durable
  evidence.
  **Generalizes:** a context-starved reviewer's large input belongs in a file it reads, not
  inlined; bound its scope with an explicit "read only this file" so broad tool access does
  not become a contamination vector. Don't commit a large, regenerable artifact when the
  deterministic command that produces it plus the verdict suffices.

## Methodological Errors Avoided

- **Did not dispatch a reviewer against an absent anchor.** The G3 `organization` reviewer
  needs a placement-map + sealed-axis clause + `tag_vocabulary` from the project's
  constitution. `discuss` (a minimal downstream adoption) declares none of those and ships no
  `lint-organization.sh`. Rather than fabricate an anchor or dispatch a reviewer that could
  only return no-oracle on everything, recorded organization as **N/A** with the reasoning
  (placements follow the conventional portable-core-mirroring layout; the `invariants`
  reviewer already covers the second-axis guard). What to do instead of forcing a gate that
  has no oracle in this project: name it N/A and say why.

## Time/Effort Wasters Identified

- **The `lint-contract-impact.sh` format is stricter than it looks** — a few minutes saved by
  reading the script before authoring. The declaration is **raw YAML at column 0** (no
  frontmatter, no markdown fence); `kind:` must be exactly `kind: added|modified|removed` with
  the value regex-anchored to end-of-line; and `impact:` must come *before* `rationale:` so the
  non-indented `rationale:` line closes the impact block in the awk parser. Reading a real
  portable-core `contract-impact.md` (016) for the on-disk shape was faster than reverse-
  engineering it from the schema prose.

## Reusable Insights

- **A `[no-oracle]` criterion that the sign-off already admitted *and* the designated
  independent reviewer adjudicated is settled — not a fresh route-to-operator.** At G3 the
  panel produced `human-residue` on exactly EARS-11 (B1 prose-fidelity) and EARS-12 (I3-negative
  absence). But those two were pre-admitted in `sign-off.md` § No-oracle Admissions, the ledger
  is operator-SIGNED (hash-bound), and the `contract-currency` reviewer — the criteria's named
  adjudicator — ran favorably (T008 affirmed 18/18 of 001's behavioral criteria reflected; G3
  found the non-subordination clause present with nothing contradicting). The
  `[no-oracle] → independent reviewer + operator` path was already fully traversed. The honest
  move is to record the residue as settled with the evidence trail, not to re-route identical,
  already-signed residue and loop. (Distinguish: a *new* no-oracle finding the operator never
  saw still routes across the seam.)

## Constraints Discovered

- **Operator-home tooling is the gate, by design — and it was present.** `lint-contract-impact.sh`
  (`~/.local/bin`) and the `contract-currency` reviewer prompt
  (`~/projects/portable-core/method/skills/independent-review/reviewers/`) both resolved, so the
  D1 floor and B1/B2 reviewer ran for real (not skipped). The two `@pytest.mark.skipif(LINT is
  None)` guards mean the D1 oracles degrade to *skip* (not false-pass) on an unprovisioned host;
  the load-bearing assumption (spec §5) held here.

## Decisions Made

- **002's contract-impact scope = framing sections only** (Overview & purpose + Methodology &
  Contract-Loop status), with 001's behavioral sections deferred to 001's own declaration.
  Alternative considered and rejected: 002 declaring all 10 sections `added` (textually true of
  its diff, but a B2 mis-declaration of behavior ownership). A future builder should not
  "simplify" this by merging the two declarations.
- **Removed the regenerable 2.25 MB `evidence-001-changeset.patch`** after the gate cleared,
  keeping `evidence-001-currency-verdict.json` as the durable evidence and the `git diff
  496e8c1^1..496e8c1` range (recorded in the tasks Review Log) as the reproduction. Alternative:
  keep the patch committed — rejected as repo bloat for a deterministically reproducible input.
- **Honored the tasks preamble's blanket `[no-review]` for T001–T007/T009** (docs/methodology,
  no production code for a G2 panel to judge), with the substantive judgment concentrated at
  T008 (currency on 001) and the full G3 panel. This is the design's call, recorded in the
  Review Log per-task rather than silently skipped.

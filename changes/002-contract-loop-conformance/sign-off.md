---
name: sign-off
purpose: Operator decision ledger — the hash-bound sign-off surface for a change
author: design agent
phase: handoff
---

# Sign-off: `contract-loop-conformance`

**Status:** Draft
**Date:** 2026-06-02

## Binding Choices

- **Fork A — conformance depth.** Chose **artifact-level adoption** over **full
  self-contained vendor**. Foreclosed: copying `lint-contract-impact.sh` + the
  `contract-currency` reviewer prompt + their tests into the `discuss` repo. Rationale:
  matches `discuss`'s existing minimal-adoption posture (it vendors no SDD-floor tooling
  either); lightest change that still yields a genuinely conforming instance; the gate runs
  from operator-home tooling on PATH. Recommendation: **accept**.
- **Fork B — treatment of change 001.** Chose **retroactive formal collapse** over
  **forward-only snapshot**. Foreclosed: synthesizing `contract.md` and leaving 001 an
  uncollapsed archive note (no gate run on it). Rationale: operator wanted the 001 collapse
  *gate-verified*; reconciled with the schema's forward-only rule because **N=1** (with one
  prior change, the genesis snapshot and 001's collapse are the same content). Recommendation:
  **accept**.
- **Sub-choice — structural oracles.** Chose **committed structural pytest oracles**
  (`tests/test_contract_conformance.py`) for the mechanical conformance facts over **carrying
  them as `[no-oracle]` gate-checks**. Foreclosed: no committed conformance tests (grep at gate
  time only). Rationale: fidelity to the project's anti-waivable-oracle discipline
  (`changes/001-…/learnings.md`); the tests are coverage-neutral (they read docs, import no
  `src`). Recommendation: **accept**.

## Load-bearing Assumptions

- **Operator-home tooling on PATH** — `lint-contract-impact.sh` and
  `independent-review`/`contract-currency` resolve from the operator's claude-home (same
  provisioning as the SDD floor). If false: the D1/B1/B2 oracles cannot run in-repo; the build
  re-escalates the scope fork (vendor the tooling — the foreclosed Fork A option), never
  silently weakens the gate.
- **N = 1** — change 001 is the only prior change, so its formal collapse equals the
  forward-only genesis snapshot. If false (more prior changes surface): only 001 is in scope;
  others remain uncollapsed archive.
- **001's merged diff is `496e8c1^1..496e8c1`** (first-parent of the 001 merge). If false: the
  currency-gate task (T008) must reconstruct the 001 changeset before the reviewer can run.

## No-oracle Admissions

- **`contract.md` faithfully reflects every behavioral criterion of change 001** (deep B1 prose
  fidelity). No oracle because: no deterministic test can prove that prose *faithfully describes*
  a behavior; this is adjudicated by the independent `contract-currency` reviewer (B1) at G3/T008
  and the operator. Every *mechanical* conformance fact (artifacts exist, declarations
  well-formed, constitution amended) does have a committed pytest oracle.

## Scope & Cost

- **Footprint** — docs/methodology only: new `contract.md`, `CHANGELOG.md`,
  `method/schemas/{contract,contract-impact,review-verdict}.md`; amended `constitution.md`;
  `changes/001-…/contract-impact.md` + a one-bullet `learnings.md` edit; the `changes/002-…/`
  package + `evidence-001-currency-verdict.json` + `tests/test_contract_conformance.py`. **No
  `src/` or production-code change** (FR-010, guarded by `test_no_src_modules_changed`); coverage
  thresholds unaffected.
- **Cost to undo** — low for the artifacts themselves (docs are revertible). The durable
  commitment is the **standing maintenance obligation**: once `constitution.md` declares the loop
  and `contract.md` exists, **every future change must keep `contract.md` current** and carry a
  `contract-impact.md`, gated at G3. That is the intended, not-cheaply-reversed consequence — it
  is the point of the change, not a side effect.

## Signature

> The `artifacts_hash` is computed over `spec.md`/`plan.md`/`tasks.md` + this ledger's body
> (everything above this `## Signature` heading). The operator stamps it via
> `sign-off.sh --feature 002-contract-loop-conformance` or by hand; design never self-stamps.

status: UNSIGNED
operator:
signed_at:
artifacts_hash:

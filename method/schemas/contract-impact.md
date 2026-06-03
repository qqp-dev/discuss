---
loop: [core]
kind: substrate
name: contract-impact
purpose: The change's authored, machine-checkable statement of how it touches the contract — the sections it adds / modifies / removes, or `none (internal-only)`. Drives the collapse step and is the contract-currency reviewer's B2 input.
author: the builder (execute/solo), at done — authored by the archiving-a-change step, beside learnings.md
phase: execute (archive / finishing)
---

# Contract-Impact Declaration

A change package carries exactly one **contract-impact declaration** at done
(`changes/NNN/contract-impact.md`). It is the change's own statement of how it touches the
contract — written at *archive*, recording *actual* impact, not the design-time
*intended* impact of `spec.md`/`plan.md`/`tasks.md`. Two consumers read it:

- **the collapse step** (`archiving-a-change`) updates **exactly** the contract sections
  the declaration names — no more, no less;
- **the `contract-currency` reviewer** uses it as the B2 (mis-declared) half of its
  two-part anchor: a declaration that contradicts the diff is a BLOCK.

It is what makes a *correctly-unchanged* contract (a pure refactor → `none`) structurally
distinguishable from a *stale* one — the distinction is decided by the
declaration-validated-against-the-diff, not by guesswork.

## Schema

A declaration has 3 fields:

| Field | Required | Shape | Meaning |
|---|---|---|---|
| **change** | yes | the change id (`016`, `017`, …) | which change this declares impact for. |
| **impact** | yes | **either** the literal `none (internal-only)` **or** a non-empty list of entries | how the change touches the contract. |
| **rationale** | yes | one line | ties the declared impact to the diff — *why* this is the impact (and, for `none`, why no behavior an acceptance criterion asserts changed). |

Each **impact list entry** has 3 fields:

| Field | Shape | Meaning |
|---|---|---|
| **section** | a contract section name | the `contract.md` section this entry collapses into. MUST name an actual section. |
| **kind** | one of `added` · `modified` · `removed` | whether the change adds a new section, modifies an existing one, or removes one. |
| **note** | one line | what changed in that section. |

`impact: none (internal-only)` asserts the change touches **no** contract section — a pure
refactor / internal-only change. It is valid **only if** the diff changes no behavior
asserted by any of the change's acceptance criteria (invariant D2); otherwise it is a
mis-declaration.

## Invariants

- **D1 — present and well-formed at done.** A completed change MUST carry a
  `changes/NNN/contract-impact.md` with all three fields, `impact` in one of the two valid
  shapes, and every list entry's `kind` from the allowed set. Checked deterministically by
  `tooling/scripts/lint-contract-impact.sh` (the floor); a missing or malformed declaration fails
  before any reviewer is dispatched.
- **D2 — consistent with the diff.** The declared impact MUST match what the diff does: a
  `none (internal-only)` declaration whose diff changes a behavior asserted by an
  acceptance criterion is invalid, and named sections MUST correspond to what the diff
  actually changed. The semantic half of D2 is judged by the `contract-currency` reviewer
  (B2); the structural half (well-formedness) by the floor.

## Worked examples

**A — `none` (a pure refactor, internal-only):**

```yaml
change: 099
impact: none (internal-only)
rationale: >
  Collapsed the two boundary guards into one range comparison; behavior is identical
  for every input, so no contract section changes and no acceptance criterion's
  asserted behavior is affected.
```

**B — multi-section (a behavior-adding change):**

```yaml
change: 100
impact:
  - section: "status command"
    kind: modified
    note: Added the --json output mode (single-line JSON object with state and since).
  - section: "Adapters"
    kind: added
    note: New "json output" adapter binding documented.
rationale: >
  The change adds a --json flag to the status command and a corresponding adapter
  binding; the "status command" section now documents both output modes and a new
  "Adapters" subsection records the binding.
```

## Probe cross-check (the reviewer reads this file)

The four fixtures of the gating dispatch probe (`tooling/tests/probes/probe-contract-currency.md`,
T001) carried declarations of exactly this shape, and the `contract-currency` reviewer
read them as its B2 input:

| Fixture | declaration | reviewer routing |
|---|---|---|
| A (`changes/099`) | `impact: none (internal-only)` | PASS (consistent with a no-op diff) |
| B (`changes/100`) | `impact: [{section: "status command", kind: modified, …}]` | PASS (matches the diff) |
| C (`changes/101`) | `impact: none (internal-only)` | **BLOCK (B2)** — `none` contradicts a behavior-changing diff |
| D (`changes/102`) | `impact: [{section: "status command", kind: modified, …}]` | BLOCK (B1, not B2) — declaration honest; the contract was stale |

All four conform to this schema by construction — the schema is the shape the probe bound.

## Cross-references

- `method/schemas/contract.md` — the contract / change-package / archive model this declaration
  is artifact 4 of.
- `method/schemas/review-verdict.md` — the verdict the `contract-currency` reviewer returns after
  reading this declaration (B2) against the diff.

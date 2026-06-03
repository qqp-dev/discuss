---
loop: [core]
kind: substrate
name: contract
purpose: The harness-agnostic Contract Loop §1 capability — the contract (current truth, one readable thing), the change package, the archive, and the propose→apply→archive lifecycle that keeps the contract true. Names what must happen; binds how (git, subagent dispatch) only in the adapter.
author: the methodology substrate; a downstream project adopts this model by copy, not a runtime link
phase: substrate (the contract + the archive) / process (the collapse lifecycle)
---

# Contract

## Overview

The **contract** is the single maintained artifact that reads as the **current truth**
of what a system does and why. It is the inversion of "reconstruct the present from a
pile of overlapping diffs": current state is always *one readable thing*, and the
generated implementation is the regenerable projection of it (Principle II). A change
is a **delta against the contract**, packaged self-contained and kept physically
separate until it **collapses** into the contract at archive — so the contract can
never silently drift.

This schema names **what** must exist and happen. It binds no harness primitive: the
two *how* bindings — git as the archive substrate, and a subagent-dispatch reviewer for
the currency gate — live in the adapter layer (Principle VII; see *Adapter-bound how*).
A downstream project adopts this model by **copying the schema**, not by a runtime link
to portable-core (see *Downstream adoption*).

The capability has **four artifacts** and **one lifecycle**.

## The four artifacts

| Artifact | Kind | What it is | Defining invariants |
|---|---|---|---|
| **Contract** | substrate | The single maintained artifact describing the current truth — what the system does and why. One readable thing; the working tree of truth. | **I1** exactly one contract exists; **I2** readable as current truth standalone, with ordinary tools, without reading the archive or the implementation; **I3** never declares itself subordinate to the archive; **I4** regenerable in equivalent form from contract + archive. |
| **Change package** | substrate | A self-contained delta against the contract: the proposal (the WHAT), the design (the HOW), the steps, the done-time records, and the working-tree diff. | **C1** physically separate from the contract until archived; **C2** carries a well-formed contract-impact declaration at done. |
| **Archive** | substrate | The lossless, append-only record of changes and their reasoning: the commit history + a human-readable change log + the retired change packages. | **A1** append-only — never mutated, lost, or corrupted; **A2** collapse adds to the contract without altering any archive member; **A3** contract + archive together regenerate an equivalent system. |
| **Contract-impact declaration** | substrate | The change's authored statement of how it touches the contract — the sections added / modified / removed, or `none (internal-only)`, with a one-line rationale. Done-time. Schema: `method/schemas/contract-impact.md`. | **D1** present and well-formed at done; **D2** consistent with the diff (a `none` declaration whose diff changes behavior asserted by an acceptance criterion is invalid). |

## The lifecycle — propose → apply → archive

A change moves through three states; only **archive** touches the contract.

| State | Who | What happens |
|---|---|---|
| **propose** | the proposer (design) | The change is expressed as a delta: the change package's proposal + design + steps are written. The contract is untouched (C1). |
| **apply** | the builder (execute/solo) | The working-tree delta is built under the project's discipline. The contract is still untouched. |
| **archive** | the builder, at finishing | The **collapse step**: (1) author the contract-impact declaration; (2) collapse the delta into **exactly the declared** contract sections, updating them to current truth; (3) leave the change package and the commit history intact. Bound into the existing finishing wrap-up — one close-out, not a bolt-on (Principle VI). |

**Lifecycle invariants:** **L1** the contract is updated *only* via the collapse step at
archive; **L2** a change reaches *done* only when the contract is current with respect to
it — enforced independently (next section), never on the builder's say-so (Principle IV).

```text
   propose ───────────► apply ───────────► archive (collapse) ───────────► done
   (change package:     (build the          (1) author contract-impact      gated on
    proposal/design/     working-tree        (2) collapse delta into the     contract
    steps; contract      delta; contract     declared contract sections      currency
    untouched — C1)      untouched)          (3) preserve archive — A2       (L2, IV)
```

## Currency enforcement (the gate)

*Done* is gated on the contract being current. A change MUST NOT be marked done while
the contract is stale with respect to it. The enforcement is an **independent,
context-starved reviewer** (a separate concern on the completion gate), judged against a
**two-part anchor** and never handed the builder's account:

- **B1 (stale):** a behavioral acceptance criterion asserts a behavior that is absent
  from the contract — the change made something true the contract does not yet describe.
- **B2 (mis-declared):** the contract-impact declaration contradicts the diff — e.g. it
  declares `none (internal-only)` although the diff changes a behavior an acceptance
  criterion asserts.

The reviewer returns a `method/schemas/review-verdict.md` object (`PASS` | `BLOCK` | `no-oracle`
residue → human). Both anchor halves are decidable from `(diff, criteria, contract
excerpt, declaration)` alone — empirically established before wiring (the gating dispatch
probe). The reviewer is **bespoke and portable**: it ships in-tree and is never delegated
to a generic code reviewer.

## Adapter-bound how (Principle VII)

Nothing above names a specific harness as load-bearing. Two bindings are **adapter-level
how**, not part of the *what*:

1. **The archive substrate is git.** "Append-only, lossless commit history + change log
   + retired packages" is the *what*; **git** (the commit log as the lossless history) is
   the portable-core binding. A downstream project MAY bind a different append-only
   substrate; the model does not depend on git.
2. **The currency reviewer's dispatch primitive.** "Spawn one context-starved reviewer
   with `(diff, criteria, contract excerpt, declaration)`" is the *what*; the harness's
   subagent-spawn primitive is the *how*. portable-core's Claude Code adapter binds it to
   the Agent/Task tool.

No contract / change-package / archive behavior here is welded to a harness primitive.

## Worked example — portable-core's own instance

portable-core is a conforming instance of this model:

| Artifact | portable-core realization |
|---|---|
| Contract | `contract.md` at the repo root — the single current-truth description of the methodology (what it is, roles, skills, schemas, the SDD flow & gates, adapters, Contract Loop status). |
| Change package | `changes/NNN/` — `spec.md` (propose) · `plan.md` + `tasks.md` (design) · `learnings.md` + `contract-impact.md` (done-time) · the working-tree diff. |
| Archive | the git commit log (lossless history) + `CHANGELOG.md` (human-readable) + the retired `changes/NNN/` packages. |
| Contract-impact declaration | `changes/NNN/contract-impact.md` (`method/schemas/contract-impact.md`). |
| Collapse step | the `archiving-a-change` capability, bound into `finishing-a-development-branch`. |
| Currency gate | the `contract-currency` reviewer on the execute/solo G3 panel. |

Forward-only: a project's historical change packages are **not** back-collapsed — they
remain archive; the contract's day-one content is a synthesized snapshot of present truth.

## Downstream adoption

A downstream project **inherits this model by adoption — copying the schema at a point in
time — not a runtime parent link** (the constitution's cross-project note: inheritance is
by reference or copy, never a binding cascade across project boundaries). The project
writes its own `contract.md`, names its own change-package shape and archive substrate,
and binds its own adapter *how*. Nothing in this schema requires portable-core to be
present at the downstream project's runtime.

## Conformance & portability check

A **conforming instance** of this model has:

1. exactly **one** contract artifact, readable as current truth standalone (I1, I2), that
   declares itself the source of truth (I3) and is regenerable from contract + archive (I4);
2. a **change-package** shape that stays separate from the contract until archive (C1) and
   carries a contract-impact declaration at done (C2);
3. an **append-only archive** the collapse never mutates (A1–A2);
4. the **propose → apply → archive** lifecycle, with collapse updating only the declared
   sections (L1) and *done* gated on currency (L2, by an independent reviewer).

**Portability holds** when, reading the *what* above, no specific harness is load-bearing:
the archive substrate (git) and the currency reviewer's dispatch primitive (a subagent
spawn) are named only in *§ Adapter-bound how* and the worked example — never in the
artifact/lifecycle definitions. A downstream project **adopts the model by copying this
schema** (and `method/schemas/contract-impact.md` + `method/schemas/review-verdict.md`) and binding its
own *how*; no runtime link to portable-core is required. portable-core's own `contract.md`
is a conforming instance (see the worked example).

## Cross-references

- `method/schemas/contract-impact.md` — the contract-impact declaration format (artifact 4; the
  reviewer's B2 input).
- `method/schemas/review-verdict.md` — the verdict the currency reviewer returns and the gate
  aggregates.

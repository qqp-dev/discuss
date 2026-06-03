---
name: sign-off
purpose: Operator decision ledger — the hash-bound sign-off surface for a change
author: design agent
phase: handoff
---

# Sign-off: `<feature-name>`

**Status:** Draft
**Date:** YYYY-MM-DD

> The operator's **decision ledger** — the sign-off surface at handoff, presented
> *instead of* the full `spec.md`. It carries the decision-shaped residue of the
> change: the four sections below are the only things the operator must accept.
> Design **accrues** these as they are decided during the flow; at handoff the
> operator **signs** the consolidated ledger (`sign-off.sh` or a hand-edit) —
> **design never stamps its own signature**. Fill each section, delete this
> guidance. An empty section is stated as `none` explicitly — never omitted.

## Binding Choices

> Genuine forks where design picked one option and foreclosed others. Each entry
> MUST name its **foreclosed alternative(s)**, the **rationale** for the pick, and
> design's **recommendation** — enough for the operator to veto or redirect in one
> turn. If the change had no genuine forks, state `none`.

- [choice] — chose X over Y. Foreclosed: Y (and Z). Rationale: … . Recommendation: accept / redirect to Y.

## Load-bearing Assumptions

> What the plan bets is true — the corpus's #1 rework cause. Each line states the
> assumption and what flips downstream if it is wrong. If the change rests on no
> load-bearing assumption, state `none`.

- [assumption] — … . If false: … .

## No-oracle Admissions

> Claims no automatable test can prove, which a human must accept (the `[no-oracle]`
> criteria). Each line states the claim and why it is unmechanizable here. If every
> criterion has a test, state `none`.

- [claim] — … . No oracle because: … .

## Scope & Cost

> What this change touches and what is expensive to undo later. State the footprint
> and any cost that is costly to reverse. If the footprint is trivial / internal-only,
> state `none` (internal-only).

- [scope] — … . Cost to undo: … .

## Signature

> Machine-readable, `grep`-parseable signature block — the FINAL section of this file.
> The `artifacts_hash` is computed over `spec.md`/`plan.md`/`tasks.md` + this ledger's
> body (everything **above** this `## Signature` heading). The operator stamps it via
> `sign-off.sh --feature <slug>` or by hand (Principle V); design never self-stamps.

status: UNSIGNED
operator:
signed_at:
artifacts_hash:

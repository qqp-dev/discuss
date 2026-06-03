# Changelog

The human-readable archive log for `discuss`. Reverse-chronological. The git commit history is
the lossless half of the archive; this file renders it for a human. Each entry corresponds to a
collapsed change package under `changes/NNN-slug/`.

## 002 — contract-loop-conformance

Adopt portable-core's **Contract Loop**: make `discuss` a conforming instance. Vendor the
schema docs by copy (`method/schemas/contract.md`, `contract-impact.md`, `review-verdict.md`);
author the genesis root `contract.md` as the single current truth (snapshotting change 001's
shipped behavior); amend `constitution.md` to declare the loop and name the `contract-currency`
reviewer as a G3 done-gate concern; seed this `CHANGELOG.md`; author per-change
`contract-impact.md` declarations for 001 and 002; and **retroactively, gate-verifiably collapse
change 001** into the contract (the `contract-currency` reviewer returns PASS). Docs/methodology
only — no `src/` change.

## 001 — discussion-draft-pipeline

Live-verified single-trigger assisted discussion-post pipeline: open a persistent logged-in
browser → navigate the fixed click-path → wait for the SPA to render → classify the landing →
select the soonest-due discussion → confirm gate → extract the prompt → hand off to a primed
Claude Code drafting session → open the draft in a GUI editor → fill the reply form **without
submitting**. Respectful-guest and human-in-the-loop throughout (no auto-submit, no stored
credentials). Shipped after two escalations that redesigned the render lifecycle and the
post-navigation auth/session-persistence handling.

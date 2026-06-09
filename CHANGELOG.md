# Changelog

The human-readable archive log for `discuss`. Reverse-chronological. The git commit history is
the lossless half of the archive; this file renders it for a human. Each entry corresponds to a
collapsed change package under `changes/NNN-slug/`.

## 004 — menu-work-modes

Split the run into an explicit work-mode menu: main-post mode drafts/edits `response.md` and
fills only the top-level reply field, while peer-reply mode extracts visible classmate posts,
drafts/edits `peer-reply-1.md` and `peer-reply-2.md`, and stops for manual paste. Added
`DISCUSS_MODE=main|peer` for non-interactive shortcuts and split the Claude workflow template
so each mode opens only the files it needs.

## 003 — editor-fill-peer-replies

Fix operator-reported run issues: default to Linux Mint Cinnamon's stock `xed --wait` editor;
harden Blackboard/Quill insertion by waiting for a visible editor, explicitly focusing/selecting
the rich-text field, inserting text, dispatching editor events, and verifying read-back; and add
first-class drafting support for the two required classmate replies by extracting visible peer
posts into `peer-posts.md`, having the primed session select two good candidates, and requiring
`peer-reply-1.md` / `peer-reply-2.md` before main-post fill. The tool still never submits and
still only fills the main top-level reply automatically; peer replies are saved for manual paste.

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

---
name: sign-off
purpose: Operator decision ledger — the hash-bound sign-off surface for a change
author: design agent
phase: handoff
---

# Sign-off: `discussion-draft-pipeline`

**Status:** Draft (post-Escalation #1 triage; G1-cleared at bounce #1)
**Date:** 2026-06-02

> The operator's decision ledger — the sign-off surface at handoff, presented *instead of*
> the full `spec.md`. The four sections below are the only things you must accept. Design
> accrues; the operator signs (`sign-off.sh --feature 001-discussion-draft-pipeline` or a
> hand-edit). Design never stamps its own signature.

> **Revision note (G1 bounce #1, 2026-06-02):** the independent G1 panel BLOCKed the first
> triage draft and design fixed it — two safety oracles (no-submit, no-creds) were rewritten
> to scan *code, not the safety prose they false-RED'd on*, and two criteria (login-pause
> FR-003, no-retry FR-016) gained real offline tests (new task T027). **No binding choice,
> assumption, no-oracle admission, or scope below changed** — the decisions are exactly what
> you reviewed; this re-signature binds them to the corrected artifacts. The panel then
> re-cleared testability + completeness; scope + sign-off-faithfulness were unaffected.

## Binding Choices

- **US1 = done; portal pipeline = PROVISIONAL.** Chose: ship the reason-and-draft engine
  (US1, no portal) as genuinely *done* and fully verified, while the portal pipeline
  (US2–US4) is built, offline-verified, and held **provisional** pending one guided live
  run (T026). Foreclosed: (a) block *all* "done" on full live verification (delays the
  value that needs no portal); (b) declare the whole thing "done" on offline oracles alone
  (the Escalation #1 mistake). Rationale: value lands immediately; the irreducibly-live
  residue is named, not hidden. **Recommendation: accept.**
- **Smooth in-tool validation (FR-017) replaces the manual ordeal.** Chose: a
  `discuss validate` guided run — log in once, press a key per checkpoint; the tool
  self-snapshots the DOM on a selector miss (FR-018). Foreclosed: the retired
  `docs/SELECTOR-CAPTURE.md` checklist + the 80-line throwaway capture script + devtools
  selector-recording. Rationale: your directive — the *human* busy work is the problem, and
  validation must be smooth. **Recommendation: accept.**
- **Offline oracles for every safety guarantee.** Chose: structural no-submit (T021),
  `file://` fill against the captured Quill form (T022), structural no-creds (T023),
  no-mock entry-point smoke (T024) — all agent work. Foreclosed: the prior
  `[no-oracle]`-everything-waivable model. Rationale: Escalation #1 corrective B; the
  `file://` fixture is a constitution-blessed controlled real boundary (§2).
  **Recommendation: accept.**
- **DEFERRED is a first-class state; the change is PROVISIONAL until T026.** Foreclosed:
  "waived renders as done." Rationale: corrective C — "all boxes checked" must never be a
  lie about the riskiest parts. **Recommendation: accept.**
- **Agentic rigor retained; coverage-% demoted.** Chose: keep TDD and *add* the oracles
  (agent work you don't run), and stop treating 100% coverage as a completeness signal (it
  never measured the seam). Foreclosed: stripping agent rigor to cut "busy work" — you
  clarified the agent's work was never your burden. **Recommendation: accept.**

## Load-bearing Assumptions

- **The captured selectors still match the *live* portal today.** If false: live
  navigate/extract/fill miss. T022's `file://` oracle still passes (it tests the captured
  snapshot), so this residue is catchable *only* by the live T026 run (or a fresh capture
  via FR-018's self-snapshot). **This is the explicit live residue you are choosing to
  defer or retire.**
- **A headless Chromium is installable for T022.** If false: T022 *loudly* skips (never
  silently); the no-submit guarantee then rests on T021's structural test alone — flagged,
  not hidden.
- **The reply field is the captured contenteditable Quill editor.** If false (a plain
  textarea on some page), runtime detection (FR-011) handles it and T022 surfaces the
  difference offline.
- **`claude` on PATH + a `--wait` GUI editor present (US1).** If false: the US1 session /
  edit step fails loud and the engine can't run; this is the one dependency US1 itself needs.

## No-oracle Admissions

- **Exactly one remains** (down from ~4 waivable safety criteria before triage): the
  live-drift / real-logged-out-page residue, validated by the T026 guided run. No offline
  test can prove today's captured selectors still match the *live* portal, or that the
  *real* logged-out UOPX page triggers the login pause — both need your authenticated live
  session. It is carried as a **DEFERRED** state, not a checkbox. Accepting the change as
  "live-unverified" = accepting this single residue.

## Scope & Cost

- **Touched by this triage:** `spec.md` (→ v0.2), `plan.md`, `tasks.md` (T009/T013/T016/T019
  downgraded to DEFERRED; Phase 8 T021–T026 added), this ledger. New test files
  (T021–T025): `test_no_submit.py`, `test_fill_offline.py`, `test_no_creds.py`,
  `test_main_smoke.py`, `test_validate.py`. `cli.py` gains a `validate` subcommand (T025) and
  smoke-testability (T024). The shipped US1 engine and the existing 53-test suite are
  untouched.
- **Cost to undo:** low — additive tests + one subcommand; nothing destructive.
- **Irreversible / external:** none. No live submit, no credential storage, no external
  publish anywhere in scope.

## Signature

> The operator stamps this (`sign-off.sh --feature 001-discussion-draft-pipeline` or by
> hand). Design never self-stamps. The floor's `lint-signoff` blocks handoff until this is
> `SIGNED` with a hash matching the current artifacts.

status: SIGNED
operator: abacus-git
signed_at: 2026-06-02
artifacts_hash: d5bc580c0362d40017d36a00c9461fe37cf6af146bfdffc034d46ed448095fce

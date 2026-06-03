---
name: learnings
feature: 001-discussion-draft-pipeline
author: execute agent
phase: compaction
---

# Learnings: `discussion-draft-pipeline`

The change shipped **live-verified** after two escalations that both attacked the same
soft target — the gap between a green gate and a working, safe program. What follows is the
record a future builder should not have to re-learn.

## Notable Challenges Overcome

- **Challenge:** "All green" was reachable for a program that did not run. The orchestrator
  was tested entirely with builder-authored fakes, and `main()` was "covered" by
  monkeypatching the very `Config.load → run` seam that was broken — so the first live
  `discuss` died with an `IndexError` on its first real line of work, having passed
  spec-match, quality, 100% coverage, and lint-ears.
  **How:** added a no-mock entry-point smoke gate (T024) that drives the REAL
  `Config.load(_load_overrides()) → run(...)` wiring to a *defined* state, stubbing only the
  outermost browser boundary. The bug site (`config.target_classes[0]`) is now exercised by
  real config on every build.
  **Generalizes:** every integration seam owns a no-mock smoke oracle. If the only test of an
  entry point mocks the functions whose *interaction* is the risk, the seam is untested by
  construction — and that is exactly where the fatal bug hides.

- **Challenge:** the first live run walked into a wall no offline test could see — a
  client-rendered ForgeRock SSO SPA. Every fixture was a *post-render* photograph; the live
  adapter read the DOM *pre-render* (`domcontentloaded` + immediate `query_selector`), so it
  saw a 1.6 KB un-painted login shell, not the discussions list. The HTML was real; it was
  real *at the wrong moment*.
  **How:** condition-based waiting (T030) — `wait_for_selector(content OR login-marker,
  bounded ~20s)` before reading — plus a pure `classify_landing` (T028) keyed on the
  pre-render shell's stable markers (`<title>Login</title>` + `data-testid="fr-body-image"`),
  and auth re-sequenced (T029) to pause *after* the first navigation where the redirect is
  actually visible.
  **Generalizes:** a fixture is honest only at the lifecycle state the production code
  observes. Before trusting captured HTML, name *when in the target's state machine it was
  captured* and confirm the code reads it at that same point — a timing mismatch is invisible
  to "is this real HTML?".

- **Challenge:** the builder's instinct ("every fix here is verifiable only live") would have
  spent the operator's live runs as the sole test harness for the auth/render redesign.
  **How:** the FR-018 self-snapshot had already produced a *real* pre-render shell artifact;
  that artifact became `fixtures/login_shell_prerender.html`, turning login-classification and
  the adapter's login→`NotAuthenticated` branch into offline, falsifiable oracles (T028 + the
  two `test_adapter_logic.py` branch oracles). Only render *timing* and session *persistence*
  stayed irreducibly live.
  **Generalizes:** a captured-on-failure artifact is not just a re-capture target — it is a
  new offline oracle. "Prove no offline oracle exists" applies recursively, including to the
  diagnostic output of the failure itself.

## Methodological Errors Avoided

- **Self-referential and waivable oracles.** A gate's green certifies only what its oracle
  *observes*. Fakes the author also wrote confirm the design agrees with itself, never that
  the integrated artifact runs; a manual checklist the operator can skip records `[x]` while
  proving nothing. Both shapes were purged: safety criteria (no-submit, no-creds) now have
  structural offline oracles, and the live residue is a distinct DEFERRED state, not a
  checkbox.
- **A self-diagnostic that fires at the broken moment inherits the bug.** FR-018's snapshot
  was a good mechanism that captured *nothing useful* because it fired pre-render, exactly as
  blind as the failure it explained. The fix moves the snapshot to *after* the render wait —
  capture where the information is present, a deliberately different point than where the
  failure tripped.

## Time/Effort Wasters Identified

- **Fixing symptoms instead of the pattern.** Escalation #1 was preceded by two in-role
  symptom fixes (a capture selector, then the config `IndexError`) before the underlying
  pattern — worthless oracle *shapes* — was named. When two consecutive fixes are the same
  kind of surprise (a thing that passed every gate yet failed in reality), stop patching and
  name the oracle gap.

## Reusable Insights

- **`is_login_page` / `classify_landing` ordering.** Check rendered content (discussion rows)
  *first*, then the login predicate, then `unknown` — so a real list is never misread as
  login, and a genuine selector miss stays distinguishable from an auth redirect. Pair login
  markers with `AND` (title *and* the ForgeRock body marker) so a page that merely has a
  "Login" title cannot false-positive; the predicate fails toward `unknown`/pause, never
  toward silently "authenticated".
- **`wait_for_selector` is a mutation-observer wait, not a poll** — it satisfies the
  Respectful-guest pace (P-I) while fixing the pre-render read. A bounded ~20s timeout
  tolerates a slow SPA paint without hanging a human-in-the-loop run.
- **Lazy imports keep the exempt adapter's live deps out of the pure module.** `portal_parse`
  (non-exempt, Playwright-free) imports selector *constants* from `portal_adapter` at module
  load; the adapter imports Playwright and `portal_parse` *inside* its live functions — so the
  offline suite imports cleanly with no Playwright installed and no constants cycle.

## Constraints Discovered

- **The live portal is a client-rendered SPA behind a ForgeRock SSO** (Blackboard Ultra,
  `vle.phoenix.edu`). The DOM is empty at `domcontentloaded`; navigation to a protected URL
  on an unauthenticated session redirects to the SSO login shell. Any "navigate then read
  immediately" adapter is wrong against this portal.
- **Session persistence requires "trust this device."** The persistent-profile model only
  survives a relaunch (no re-2FA) if the operator selects "keep me signed in / trust this
  device" at login so ForgeRock issues persistent SSO cookies. T031 verified this holds live;
  had it failed, the fallback (attach to the operator's running browser via CDP) was a
  spec-level fork to re-escalate, not silently adopt.

## Decisions Made

- **"Waived" and "deferred" are not "done."** DEFERRED is a first-class, visible state; a
  change carrying an unrun live safety check is PROVISIONAL, not done. T026/T031 were
  operator-run and only then recorded live-verified — explicitly the operator's attestation,
  never agent self-certification. A future builder must not collapse a live residue into a
  checked box to make the change "look done".
- **Defer a live residue by its *shape*, not its cheapest case.** Escalation #1's residue was
  framed as a one-file selector-value swap; the real shape was a cross-cutting
  render+auth+session redesign. When deferring irreducibly-live work, enumerate the *kinds* of
  failure it stands in for (value drift? rendering lifecycle? auth flow? session lifetime?) so
  the recovery budget matches the blast radius.
- **Contract-collapse recorded N/A, then retroactively closed.** At 001's done-time this project
  was a minimal portable-core adoption with no `contract.md` / contract-impact schema / currency
  reviewer / lint vendored, so rather than invent that substrate (design's lane) the change's
  behavioral record stayed in `spec.md` v0.3 + the tasks Review Log + this package, with a note
  that a future builder who *does* vendor the Contract Loop should collapse 001's criteria into a
  new `contract.md`. **Change 002 (`contract-loop-conformance`) did exactly that:** it vendored
  the Contract Loop, authored the genesis `contract.md`, and retroactively, gate-verifiably
  collapsed 001 into it — see `changes/001-discussion-draft-pipeline/contract-impact.md` (the
  authored declaration that replaces this N/A) and the `contract-currency` reviewer's recorded
  PASS in the 002 package.

---
name: spec
purpose: Feature specification
author: design agent
phase: specify
---

# Spec: `discussion-draft-pipeline`

**Status:** Draft (v0.3 — post-Escalation #2 triage)
**Date:** 2026-06-02
**Author:** design agent

## 0. Reader's Guide

`discuss` turns a single operator trigger into an assisted discussion-post draft. Read
§1 for the problem and shape, §2 for the four prioritized slices (the **core
reason-and-draft engine is the MVP** and is testable without any portal automation), §3
for the numbered requirements, and §4 for the EARS criteria the review gates judge
against. The one load-bearing risk — an unknown, login-gated, proprietary portal DOM —
is called out in §3.3, §5, and is quarantined by design (Constitution P-III).

## 1. Vision & Goals

### 1.1 The problem
A UOPX student writing a weekly discussion post wants to think the topic through *with*
a language model and produce **their own** response — not have it ghostwritten. Doing
this by hand means: log into the portal, click into the class, find the discussion due
this week, copy the prompt out, paste it into a chat tool, draft, edit, then paste back
into the reply box. Every copy/paste is friction and a chance to land text in the wrong
place.

### 1.2 The goal
One trigger that: finds the discussion with the soonest upcoming due date in the
logged-in portal, pulls its prompt, runs a Claude Code session that helps the student
reason about the topic and drafts from *their* input, opens that draft in a GUI editor
for final edits, and fills the result into the reply form — **stopping before submit**
so the student reviews and posts. A respectful guest on the portal; human-in-the-loop
throughout.

### 1.3 Success Criteria
1. From one trigger, the operator reaches an edited draft sitting in the correct
   discussion's reply form (unsubmitted), with no manual copy/paste at either end.
2. The core reason-and-draft engine delivers value on its own (prompt in by hand →
   edited response out) before any portal automation exists.
3. The tool never submits a reply and never stores credentials.

### 1.4 Non-goals
- **No auto-submit.** The operator always performs the final post (Constitution P-II).
- **No credential automation / no scraping.** Reuse the operator's live session only
  (P-I); no login-form filling, no crawling beyond the fixed click-path.
- **No multi-discussion batching.** One discussion (the soonest-due) per run.
- **No portal other than UOPX.** Selectors target one portal; generality is out of scope.
- **No grade/feedback reading, no thread-reply-to-peers.** Only the operator's own
  initial post to the prompt.

## 2. User Scenarios & Testing *(mandatory)*

### User Story 1 — Reason-and-draft engine (Priority: P1) 🎯 MVP

The operator has a discussion prompt (initially provided by hand). They run the session;
it surfaces the prompt's key angles and tensions, asks for their stance, points, and any
reading/evidence, drafts a response grounded in their answers, then opens that draft in a
GUI editor. The operator edits and closes; the saved file is the final response.

**Why this priority**: This is the value engine. It works standalone with manual
prompt-in / response-out, so it's a viable tool before any fragile portal coupling
exists — and it's the part that honors "reason about the topic with assistance."

**Independent Test**: Place a sample prompt in the run dir, launch the session, complete
the dialogue + edit, and confirm a coherent `response.md` reflecting the operator's input
exists. No browser involved.

**Acceptance Scenarios**:
1. **Given** a prompt file in a fresh run dir, **When** the operator runs the session and
   completes the dialogue, **Then** a draft is written and the GUI editor opens on it.
2. **Given** the editor is open on the draft, **When** the operator saves and closes,
   **Then** the saved file is treated as the final response and the session exits.

---

### User Story 2 — Auto-discover & extract the target prompt (Priority: P2)

From the logged-in portal, the tool walks the fixed click-path (class → discussions),
reads the listed due dates, selects the discussion with the soonest upcoming due date,
shows a confirmation gate naming it, and on confirm extracts the plaintext prompt into
the run dir for US1.

**Why this priority**: Removes the front-end copy/paste. Builds on US1 by feeding it the
prompt automatically. Independently demonstrable.

**Independent Test**: With a logged-in profile, run discovery+extraction and confirm (a)
it lands on the discussion whose due date is soonest, (b) the confirmation names that
discussion, (c) the extracted text matches the prompt shown on the page. Parsing/selection
logic is additionally tested against saved-HTML fixtures.

**Acceptance Scenarios**:
1. **Given** a logged-in session with several discussions, **When** discovery runs,
   **Then** the discussion with the soonest upcoming due date is selected and named in the
   confirmation gate.
2. **Given** the confirmation gate, **When** the operator declines, **Then** the run
   aborts without extracting anything.
3. **Given** the operator confirms, **When** extraction runs, **Then** the prompt
   plaintext is written to the run dir.

---

### User Story 3 — Fill the reply form (no submit) (Priority: P3)

Given a final response and the target discussion page still open, the tool locates the
reply field, detects whether it is a plain textarea or a rich-text/contenteditable
editor, injects the text, verifies by reading the rendered content back, and stops —
leaving it unsubmitted for the operator to review and post.

**Why this priority**: Removes the back-end copy/paste and closes the loop. The riskiest
injection surface, so it ships after the value engine and extraction are proven.

**Independent Test**: With the target page open and a known response, run fill and confirm
(a) the rendered field content equals the response, (b) nothing was submitted (the post is
not live), (c) an undetectable field aborts write-back while preserving the response file.

**Acceptance Scenarios**:
1. **Given** a target discussion page and a final response, **When** fill runs, **Then**
   the reply field's rendered content equals the response and the post is NOT submitted.
2. **Given** a reply field the adapter cannot locate or whose read-back differs, **When**
   fill runs, **Then** write-back aborts, the response file is preserved, and the operator
   is told to paste manually.

---

### User Story 4 — One-click end-to-end (Priority: P4)

A desktop launcher (and a `discuss` command) runs the whole pipeline: open the persistent
browser, handle login if needed, discover+confirm+extract (US2), run the session (US1),
fill the reply (US3), and report. This is the wiring slice.

**Why this priority**: The "click a shortcut" UX. Depends on US1–US3 existing.

**Independent Test**: Click the launcher and observe the full flow end-to-end against the
live portal, ending with the reply field filled and unsubmitted on the correct discussion.

**Acceptance Scenarios**:
1. **Given** a logged-in profile, **When** the operator clicks the launcher, **Then** the
   full pipeline runs to a filled, unsubmitted reply on the soonest-due discussion.
2. **Given** the operator is logged out, **When** a run starts, **Then** the tool pauses
   for manual login and then continues.

### Edge Cases

- **Nothing due** (no upcoming discussion / all past): stop and report; never guess or
  pick a past one.
- **Tie on soonest due date**: deterministic tiebreak (earliest due, then listing order),
  surfaced in the confirmation gate so the operator decides; documented, not silent.
- **Operator already posted** to the soonest-due discussion: selection is by due date
  only; the confirmation gate lets the operator decline and the run ends cleanly.
  (Skipping already-answered discussions is a deliberate non-goal for v1.)
- **Logged out / session expired mid-run**: a portal navigation redirects to the SSO login;
  detect the login landing *after* navigation, pause and prompt for manual login in the same
  context, retry the navigation once, then resume; never automate the login form (FR-003).
- **Navigation lands on an un-rendered SPA shell**: the portal is client-rendered, so the
  DOM read immediately after `goto` may be an empty/login shell. Wait for the rendered
  content (discussion rows *or* the login marker) within a bounded human-paced timeout
  before classifying; never treat a pre-render read as a selector miss (FR-004).
- **Session does not persist across launches (would force re-2FA every run)**: this is a
  *blocking* live finding, not a silent degradation — if a subsequent run lands back on the
  login shell, the persistence premise (FR-002) is broken; surface it (SC-008) and do not
  mark the change live-verified. Contingency if unfixable: attach to the operator's already
  authenticated running browser (a spec-level change, re-decided, not assumed here).
- **Portal markup changed (selector miss)**: fail loud naming the exact failing step;
  the fix is confined to the adapter module (P-III).
- **Reply field is neither a known textarea nor a known rich-text editor**: abort
  write-back, preserve `response.md`, instruct manual paste (FR-012).
- **Editor closed without saving / empty or whitespace-only response**: do not touch the
  form; report.
- **Session aborted by the operator (Ctrl-C) before completion**: no write-back; any
  partial draft on disk is preserved.
- **Unparseable due date** on a listed discussion: treat as not a valid target, skip it
  for selection, and report if it would have been chosen.
- **Transient page-load timeout**: a single bounded, human-paced retry is permitted; a
  second failure stops the run (no retry-storm — P-I).
- **Multiple classes**: the target class is configurable; selection is soonest-due within
  the configured class(es).

## 3. Requirements *(mandatory)*

### 3.1 Functional Requirements

- **FR-001**: The tool MUST be launchable from a single operator trigger (a desktop
  launcher and an equivalent `discuss` command) that starts the orchestrator and opens a
  terminal for the interactive session.
- **FR-002**: The tool MUST drive the portal through a tool-owned **persistent** browser
  profile that reuses the operator's existing authenticated session, and MUST NOT store
  credentials anywhere. **Session reuse is load-bearing (Escalation #2): a subsequent run
  within the session's validity window MUST NOT require a fresh manual login NOR a repeated
  two-step verification — the persistent profile MUST carry the operator's SSO /
  trusted-device session across launches.** IF the portal's session genuinely cannot
  persist across separate launches (so the operator would re-do 2FA every run), that is a
  **blocking live finding** (SC-008), surfaced — never folded into "done".
- **FR-003**: IF a portal navigation lands on the login screen (the operator is not
  authenticated, or the session expired), THEN the tool MUST pause and prompt for manual
  login in the browser window **after that navigation, within the same browser context**,
  then **retry the navigation once** and continue — it MUST NOT automate credential entry.
  The auth check MUST run **after the first portal navigation** (where a login redirect is
  observable), NOT against the pre-navigation blank page (where no redirect is yet visible);
  the manual-login pause is meaningless if it fires before navigation (Escalation #2).
- **FR-004**: The tool MUST navigate the fixed click-path (class → discussions), **wait for
  the discussions content to render** (the portal is a client-rendered SPA — the DOM MUST
  NOT be read pre-render), and select the discussion with the **soonest upcoming due date**
  within the configured class(es).
- **FR-005**: The tool MUST present a confirmation gate naming the selected discussion and
  its due date before extracting, and MUST abort cleanly if the operator declines. The
  gate is on by default and configurable off.
- **FR-006**: The tool MUST extract the plaintext discussion prompt from the selected
  discussion page into the run dir.
- **FR-007**: The tool MUST hand the extracted prompt to an interactive Claude Code session
  primed (via a workflow `CLAUDE.md`) with the reason-with-student → draft → edit workflow.
- **FR-008**: The primed session MUST surface the prompt's key angles, draw out the
  operator's stance/points/evidence, and ground the draft in that input before opening the
  editor (it MUST NOT silently auto-generate without operator input).
- **FR-009**: The session MUST open the draft in a GUI editor and block until the operator
  saves and closes; the saved file is the final response.
- **FR-010**: The tool MUST fill the final response into the reply form on the same
  discussion page and MUST NOT submit/post it.
- **FR-011**: The reply-form fill MUST detect the field type (plain textarea vs
  rich-text/contenteditable) **at runtime** and handle both; the type MUST NOT be
  hard-coded.
- **FR-012**: After filling, the tool MUST verify by reading the field's rendered content
  back and comparing to the intended text; IF the field cannot be located OR the read-back
  differs, THEN write-back MUST abort, the response file MUST be preserved on disk, and the
  operator MUST be told to paste manually.
- **FR-013**: Every UOPX-specific selector and the click-path MUST be isolated in a single
  adapter module; no portal selector may appear elsewhere.
- **FR-014**: On any failure (logged out, nothing due, selector miss, empty draft,
  read-back mismatch), the tool MUST stop and report the specific failing step; it MUST NOT
  retry-storm or proceed on a guess. (At most one bounded human-paced retry on a transient
  load timeout.)
- **FR-015**: The final response MUST always be persisted to disk (the run dir) so it is
  never lost if any downstream step fails.
- **FR-016**: A run MUST operate at human pace and touch the minimum number of pages
  required by the fixed click-path (Respectful-guest, Constitution P-I).
- **FR-017**: All human-facing setup and live validation MUST be **tool-driven and
  in-tool**: the tool itself performs each live step and the operator confirms via a
  single keypress at the visual checkpoint. The tool MUST NOT require the operator to run
  throwaway capture scripts, hand-save HTML fixtures, inspect the DOM in devtools, or work
  through a separate manual checklist. The operator's only irreducible manual acts are (a)
  logging into the portal by hand once when the tool opens the browser (P-I), and (b)
  eyeballing and confirming a single guided validation run (`discuss validate`).
- **FR-018**: WHEN a selector fails to match the live portal, the tool MUST snapshot the
  current page markup to a fixture file **itself** (for re-capture and offline
  re-verification) and report which step failed naming the adapter as the one-file fix —
  the operator MUST NOT hand-capture markup. **The snapshot MUST be taken after the page has
  rendered (post-wait), so the diagnostic captures the rendered DOM rather than an
  un-rendered SPA shell** (Escalation #2: the first self-snapshot captured a 1.6 KB
  pre-render login shell because it fired at the same pre-render instant the miss was
  detected — a diagnostic that fires at the broken moment inherits the bug).

### 3.2 Key Entities

- **Run**: one invocation. Owns a per-run directory containing `prompt.md` (extracted
  prompt + metadata), the rendered workflow `CLAUDE.md`, and `response.md` (the final
  text). Carries the selected discussion's title, due date, and URL.
- **Target discussion**: the selected discussion — title, due date, page URL, and (at
  write-back) a located reply-field handle with a detected type.
- **Portal adapter**: the single module holding all UOPX selectors and the click-path,
  plus the runtime field-type detection. Pure parsing/selection logic is factored into a
  separate, fully-tested `portal_parse` unit operating on HTML/text strings.

### 3.3 The load-bearing assumption (called out)

The UOPX portal is a **proprietary, login-gated DOM we do not control and cannot guess**.
Real selectors for the click-path, prompt extraction, and the reply field are **captured
against the live logged-in portal during build** (a setup/verification task — see
`tasks.md`), not invented in this spec. The reply-field type is unknown until inspected,
hence FR-011's runtime detection. This assumption is the project's top break risk; it is
contained by FR-013 (one adapter module) and re-verified whenever the portal changes.

**Offline oracles retire "our code is wrong"; they do not retire "the live portal
drifted."** Driving the real adapter against the captured fixtures (via `file://`) proves
our field-type detection, read-back, and no-submit *logic* is correct against the markup
we captured — and the structural tests prove no submit/credential path exists in any
build. What no offline test can prove is that today's captured selectors still match the
*live* portal, or that the *real* logged-out page still triggers the login pause; that
residue is irreducibly live. The method's failure in Escalation #1 was to let that residue
hide behind `[no-oracle]` green and a waivable checklist. It is now surfaced as named,
deferred, tool-driven validation runs (T026, T031) — never silently folded into "done".

**The shape of the live residue (Escalation #2 correction).** The deferred-live risk was
first described only as "do today's captured selectors still match" — i.e. a one-file
selector-*value* swap with a one-file recovery. The first live run proved the residue's
true shape is **architectural, not value-level**, across three axes, and a deferred-live
item must name all of them so recovery is provisioned for the real blast radius (not the
cheapest imagined one):

1. **Rendering lifecycle.** The portal (Blackboard Ultra) and its IdP (ForgeRock) are
   *client-rendered SPAs*; every captured fixture is a *post-render* snapshot, but the
   adapter read the DOM *pre-render*. A real fixture is honest only at the lifecycle state
   the production code observes — post-render markup is a faithful photo of a state the
   live code never reads first. (FR-004 now mandates waiting for render; FR-018 now snapshots
   post-render.)
2. **Auth flow.** Navigating to a portal URL on an unauthenticated session *redirects to the
   SSO login*; the auth check must run *after* navigation, in the same context, and retry
   (FR-003). A pre-render login shell carries none of the post-render markers, so login
   detection must key on the pre-render shell too — and, crucially, the captured shell
   (`evidence-navigate_live.html`) makes that an **offline** oracle, not a live one.
3. **Session lifetime.** "The session persists across launches" was a silent, load-bearing
   *environment* assumption. If false, the operator re-does manual login — possibly
   **two-step verification** — every run, which is unacceptable (operator directive,
   Escalation #2). FR-002/SC-008 now make persistence-without-re-2FA a blocking, measurable
   live requirement, not an assumed convenience.

## 4. Success Criteria *(mandatory)*

### 4.1 Measurable Outcomes

- **SC-001**: In a single triggered run on a logged-in profile, the operator ends with an
  edited draft filled into the soonest-due discussion's reply form, unsubmitted, with zero
  manual copy/paste.
- **SC-002**: A change to any single portal selector is fixable by editing exactly one
  module (`portal_adapter.py`); no other source file changes.
- **SC-003**: No run path ever clicks submit/post, and no credential is ever written to
  disk.
- **SC-004**: Non-exempt modules (parsing/selection, orchestration, run-dir/handoff) meet
  the Constitution §1 coverage thresholds (line 85 / branch 75), exercised against
  saved-HTML fixtures and mocked-adapter orchestration tests.
- **SC-005**: The operator's manual validation footprint is **zero throwaway scripts,
  zero hand-saved fixtures, and zero devtools inspection** — validation is one tool-driven
  `discuss validate` run gated on single-keypress confirmations (FR-017).
- **SC-006**: A real `discuss` invocation reaches a **defined** pipeline state through the
  genuine entry-point wiring (`Config.load → _load_overrides → run`) with only the live
  browser/portal stubbed at the outermost boundary — i.e. the program provably *runs*; the
  integration seam is gated by a no-mock smoke test, never by fakes of its own internals.
- **SC-007**: No acceptance criterion encoding a **safety guarantee** (no-submit,
  no-credentials) is waivable-into-"done": each has an automatable offline oracle, and any
  irreducibly-live residue renders as an explicit **deferred / live-unverified** state
  distinct from "done", never as a checked box.
- **SC-008**: A run subsequent to an authenticated run, within the session's validity
  window, reaches the discussions list **without a fresh manual login and without repeating
  two-step verification** (the FR-002 persistence guarantee, made measurable post-Escalation
  #2). If the tool-owned persistent profile cannot carry the session across launches, that
  is surfaced as a **blocking live finding**, never folded into "done"; the change stays
  PROVISIONAL until persistence-without-re-2FA is confirmed (T031) or an explicit
  alternative auth model is accepted.

### 4.2 Acceptance Criteria (EARS)

> **Oracle honesty (post-Escalation #1).** Every criterion below carries an *automatable*
> oracle. The two formerly `[no-oracle]` safety criteria (no-credentials, login-pause) and
> the human-pace criterion now have real offline tests; no-submit gains a *structural*
> oracle on top of the orchestrator-level one; and the reply-fill logic is exercised
> against the captured Quill fixture via `file://` (a controlled real boundary,
> Constitution §2). **Post-Escalation #2** adds two more *offline* oracles the first pass
> wrongly assumed were live — login-shell classification (the captured pre-render ForgeRock
> shell `evidence-navigate_live.html` is a real fixture) and post-navigation auth sequencing
> (flow logic via the no-mock smoke). What remains irreducibly live — *does the SPA render in
> time, and does the persistent session survive a relaunch without re-2FA* — is **not**
> hidden here as `[no-oracle]`; it is named **deferred / live-unverified** items (T026 guided
> run, T031 persistence run), distinct from "done" (SC-007/SC-008).

```ears
WHEN the operator triggers a run and is authenticated, the tool SHALL select the discussion with the soonest upcoming due date. [test: test_select_soonest_due_from_fixture]
WHEN a discussion is selected, the tool SHALL display a confirmation naming that discussion and its due date before extracting. [test: test_confirm_gate_names_discussion]
WHEN the operator declines the confirmation gate, the tool SHALL abort the run without extracting anything. [test: test_confirm_decline_aborts]
WHEN the operator confirms the gate, the tool SHALL write the extracted plaintext prompt to the run dir. [test: test_extracted_prompt_written]
IF no discussion has an upcoming due date, THEN the tool SHALL stop and report rather than select a past or arbitrary discussion. [test: test_no_upcoming_due_stops]
WHEN the primed session completes with a saved edited draft, the tool SHALL fill that text into the reply form without submitting it. [test: test_fill_does_not_submit]
The reply-fill code path SHALL contain no submit/post-control lookup or click. [test: test_fill_reply_has_no_submit_path]
WHEN filling the captured reply form offline via file://, the tool SHALL detect the field type at runtime, fill it, pass read-back, and submit nothing. [test: test_fill_against_captured_reply_form]
IF the reply field cannot be located or the read-back does not equal the intended text, THEN the tool SHALL abort write-back, preserve the response file, and instruct the operator to paste manually. [test: test_fill_verify_mismatch_aborts]
The tool SHALL write no portal credential to disk and SHALL touch only the persistent profile directory for session state. [test: test_no_credentials_persisted]
IF the operator is not authenticated when a run starts, THEN the tool SHALL pause and prompt for manual login before proceeding. [test: test_ensure_logged_in_pauses_on_login_page]
WHILE a run is in progress, the tool SHALL act at human pace and SHALL NOT issue an automated retry loop on a selector miss. [test: test_no_retry_loop_on_selector_miss]
The tool SHALL confine every portal-specific selector to a single adapter module. [test: test_selectors_confined_to_adapter]
The tool SHALL persist the final response to disk before attempting write-back. [test: test_response_persisted_before_fill]
WHEN discuss is invoked with a valid configuration, the tool SHALL reach a defined pipeline state through the real entry-point wiring and SHALL NOT crash in the integration seam. [test: test_main_smoke_reaches_defined_state]
WHEN the operator runs guided validation, the tool SHALL drive each live check itself and gate it on a single-keypress operator confirmation. [test: test_guided_validation_uses_single_keypress_confirms]
WHEN a portal navigation lands on the client-rendered login shell, the tool SHALL classify it as a login page from the pre-render markup (not as a selector miss). [test: test_classify_prerender_login_shell]
WHEN a portal navigation lands on the login page, the tool SHALL pause for manual login after navigation and retry the navigation once in the same context before proceeding, and SHALL NOT run the auth check before the first portal navigation. [test: test_auth_pause_is_post_navigation_with_retry]
WHEN navigating a portal page, the tool SHALL wait for the rendered content (discussion rows or the login marker) within a bounded human-paced timeout and SHALL NOT read or snapshot the DOM pre-render. [no-oracle]
WHEN a subsequent run starts after a prior authenticated run within the session's validity window, the tool SHALL reach the discussions list without a fresh manual login or repeated two-step verification. [no-oracle]
```

## 5. Assumptions

- The operator runs Linux with a desktop environment (for the launcher and a `--wait`
  capable GUI editor) and has Claude Code (`claude`) on PATH.
- The operator logs into UOPX by hand once in the tool's persistent profile; the session
  then **persists across separate launches** until it expires — i.e. a later run does NOT
  re-prompt login or two-step verification. **(Load-bearing and unvalidated as of Escalation
  #2 — the live evidence is ambiguous; this is now a blocking live check, T031/SC-008, not an
  assumed convenience. If the SSO session cannot persist across launches, the tool-owned
  persistent-profile model fails and the contingency is attaching to the operator's already
  authenticated running browser — a re-decided spec change, not assumed here.)**
- The portal is a **client-rendered SPA** (Blackboard Ultra over a ForgeRock IdP): the DOM
  must be read after it renders, never immediately after navigation (Escalation #2).
- Discussions list a parseable due date in the discussions view (basis for selection).
- The prompt content is plaintext once the discussion page is reached (stated by operator).
- A `--wait`-capable GUI editor is available/configurable (default candidate: `code
  --wait`, with a configurable fallback).
- "Soonest upcoming due date" means the nearest future due date; past-due discussions are
  not selected.

## 6. Dependencies

- Claude Code CLI (`claude`) available and authenticated under the operator's session.
- Playwright (Python) with a browser able to maintain a persistent profile.
- The live UOPX portal, reachable via the operator's authenticated session (selectors
  captured during build — §3.3).

## 7. Glossary

- **Run dir:** per-invocation working directory holding `prompt.md`, the rendered workflow
  `CLAUDE.md`, and `response.md`.
- **Portal adapter:** the single module isolating all UOPX selectors, the click-path, and
  runtime reply-field-type detection.
- **Confirmation gate:** the pre-extraction prompt naming the selected discussion + due
  date; the cheap human checkpoint against wrong-target.
- **Write-back:** filling the final response into the reply form without submitting.

## 8. Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | 2026-06-01 | design agent | Initial spec. |
| 0.2 | 2026-06-02 | design agent | Escalation #1 triage. Added FR-017 (smooth in-tool human validation), FR-018 (tool self-captures markup on selector miss); replaced the 3 waivable `[no-oracle]` safety/pace criteria with automatable offline oracles + the structural no-submit and no-creds oracles + the file:// fill oracle + the no-mock smoke oracle; added SC-005..007 (zero human busy-work, program-provably-runs, safety-not-waivable-into-done); §3.3 offline-vs-live-residue honesty note. |
| 0.3 | 2026-06-02 | design agent | Escalation #2 triage (assumption failure: client-rendered SPA + post-navigation SSO redirect + non-persistent session). FR-002 strengthened (persistence without re-2FA is load-bearing/blocking), FR-003 re-sequenced (pause *after* navigation, in-context retry), FR-004 (wait for render), FR-018 (snapshot post-render). Added SC-008 (persistence/no-re-2FA blocking live check) and 4 EARS criteria (2 offline: login-shell classification, post-nav auth sequencing; 2 live: render-wait, persistence). §3.3 now names the three-axis shape of the live residue (rendering lifecycle / auth flow / session lifetime). |

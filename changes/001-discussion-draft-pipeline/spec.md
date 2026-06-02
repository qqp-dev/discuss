---
name: spec
purpose: Feature specification
author: design agent
phase: specify
---

# Spec: `discussion-draft-pipeline`

**Status:** Draft
**Date:** 2026-06-01
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
- **Logged out / session expired mid-run**: pause and prompt for manual login, then
  resume; never automate the login form.
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
  credentials anywhere.
- **FR-003**: IF the operator is not authenticated, THEN the tool MUST pause and prompt
  for manual login in the browser window, then continue — it MUST NOT automate credential
  entry.
- **FR-004**: The tool MUST navigate the fixed click-path (class → discussions) and select
  the discussion with the **soonest upcoming due date** within the configured class(es).
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

### 4.2 Acceptance Criteria (EARS)

```ears
WHEN the operator triggers a run and is authenticated, the tool SHALL select the discussion with the soonest upcoming due date. [test: test_select_soonest_due_from_fixture]
WHEN a discussion is selected, the tool SHALL display a confirmation naming that discussion and its due date before extracting. [test: test_confirm_gate_names_discussion]
IF the operator is not authenticated when a run starts, THEN the tool SHALL pause and prompt for manual login before proceeding. [no-oracle]
WHEN the operator declines the confirmation gate, the tool SHALL abort the run without extracting anything. [test: test_confirm_decline_aborts]
WHEN the operator confirms the gate, the tool SHALL write the extracted plaintext prompt to the run dir. [test: test_extracted_prompt_written]
WHEN the primed session completes with a saved edited draft, the tool SHALL fill that text into the reply form without submitting it. [test: test_fill_does_not_submit]
IF the reply field cannot be located or the read-back does not equal the intended text, THEN the tool SHALL abort write-back, preserve the response file, and instruct the operator to paste manually. [test: test_fill_verify_mismatch_aborts]
IF no discussion has an upcoming due date, THEN the tool SHALL stop and report rather than select a past or arbitrary discussion. [test: test_no_upcoming_due_stops]
WHILE a run is in progress, the tool SHALL act at human pace and SHALL NOT issue automated retry loops against the portal. [no-oracle]
The tool SHALL store no portal credentials on disk. [no-oracle]
The tool SHALL confine every portal-specific selector to a single adapter module. [test: test_selectors_confined_to_adapter]
The tool SHALL persist the final response to disk before attempting write-back. [test: test_response_persisted_before_fill]
```

## 5. Assumptions

- The operator runs Linux with a desktop environment (for the launcher and a `--wait`
  capable GUI editor) and has Claude Code (`claude`) on PATH.
- The operator logs into UOPX by hand once in the tool's persistent profile; the session
  persists across runs until it expires.
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

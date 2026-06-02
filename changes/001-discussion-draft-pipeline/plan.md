---
name: plan
purpose: Implementation plan
author: design agent
phase: plan
---

# Plan: `discussion-draft-pipeline`

**Status:** v1
**Date:** 2026-06-01
**Companion to:** `spec.md` and `tasks.md`

**Goal:** A single-operator Python tool that, on one trigger, drives a logged-in UOPX
portal to the soonest-due discussion, runs an assisted reason-and-draft Claude Code
session, lets the operator edit in a GUI editor, and fills the result into the reply form
without submitting.

**Architecture:** One linear, sequential orchestrator process. The orchestrator owns the
browser (Playwright persistent context); the Claude Code session owns the reasoning/text.
They never run concurrently — the orchestrator brackets a blocking interactive `claude`
subprocess and hands off through files (`prompt.md` in, `response.md` out). All portal
coupling is quarantined; pure parsing is separated from live I/O so it can be honestly
tested.

**Tech Stack:** Python 3.11+, Playwright (sync API, persistent context), pytest, a
freedesktop `.desktop` launcher, a `--wait`-capable GUI editor.

## 1. Tech Choices

| Concern | Choice | Rationale |
|---------|--------|-----------|
| Language / runtime | Python 3.11+ | Operator choice; first-class Playwright bindings; natural for CLI orchestration, `subprocess`, and file handoff. |
| Browser automation | Playwright **sync** API, **persistent context** (`launch_persistent_context`) | Persistent profile dir reuses the operator's live auth session (FR-002, P-I); sync API keeps the linear pipeline simple. |
| Packaging / entry point | `pyproject.toml` with a `discuss` console-script | Gives the `discuss` command the launcher invokes (FR-001). |
| Session orchestration | `subprocess.run(["claude"], cwd=run_dir)` — interactive, **blocking** | Clean sequential handoff; orchestrator resumes for write-back when the session exits. |
| Priming the session | `claude` launched **with cwd = run dir**, which contains the rendered `CLAUDE.md` (the workflow) and `prompt.md` | Claude Code auto-reads `CLAUDE.md` from cwd; no fragile flag contract. |
| Data handoff | Files in a per-run dir: `prompt.md` (in), `response.md` (out) | Simple, debuggable, durable (FR-015); no concurrency/IPC. |
| Editor | Configurable `--wait`-capable GUI editor; default candidate `code --wait`, fallback configurable | Prose editing; save+close is the unambiguous "submit" signal (FR-009). The session opens it via Bash and blocks. |
| Launcher | freedesktop `.desktop` entry → `launcher/launch.sh` → opens a terminal running `discuss` | The literal "click a shortcut" UX (FR-001). |
| Pure HTML parsing | Parse saved/markup strings with `selectolax` (or `lxml`) in `portal_parse.py` | Keeps due-date parsing + selection + prompt extraction pure and unit-testable against saved fixtures (Constitution §2). |
| Live DOM access | Playwright **locators** in `portal_adapter.py` | The live surface; exempt from coverage, verified by operator checklist. |
| Testing | pytest; saved-HTML fixtures (parsing), mocked adapter (orchestration), operator checklist (live) | Honest oracles per Constitution §2; never mock the system under test. |

## 2. Architecture Decisions

- **Linear sequential pipeline; orchestrator brackets the session.** The orchestrator runs
  the browser steps, blocks on the interactive `claude` subprocess, then resumes for
  write-back. *Alternatives considered:* give the agent an MCP tool to drive the browser
  itself — rejected (YAGNI; more moving parts; harder to keep bounded and respectful for a
  one-operator tool).
- **Split portal code into two modules.** `portal_adapter.py` = live Playwright I/O
  (navigate/extract/fill, runtime field-type detection) + the selector constants;
  `portal_parse.py` = pure functions on HTML/text strings (parse due dates, choose
  soonest-due, extract prompt text). *Alternative:* one fused module — rejected: parsing
  could not then be honestly unit-tested without mocking the live system (Constitution §2).
- **Runtime reply-field-type detection** (textarea vs contenteditable/rich-text), never
  hard-coded (FR-011) — the field type is unknown until we inspect the live portal.
- **Verify-by-read-back for every fill** (FR-012, P-IV): after injecting, read the rendered
  field content and compare; on mismatch/not-found, abort write-back, preserve
  `response.md`, instruct manual paste. `fill()` returning is never treated as success.
- **Persistent browser context for the whole run**, single page reused for write-back so
  the same discussion page that was extracted from is the one filled.
- **Confirmation gate default-on** (FR-005) — the cheap human checkpoint against
  wrong-target; configurable off in `config.py`.
- **Fail-loud, no retry-storm** (FR-014, P-I): typed errors name the failing step; at most
  one bounded human-paced retry on a transient load timeout.

### File structure

```
discuss/
  pyproject.toml
  src/discuss/
    __init__.py
    cli.py            # `discuss` entry point + the orchestrator/pipeline (wires US1–US3)
    config.py         # profile dir, target class id(s), confirm flag, editor cmd, run-root
    browser.py        # [COVERAGE-EXEMPT] persistent-context lifecycle + login detection/pause
    portal_adapter.py # [COVERAGE-EXEMPT] live navigate/extract/fill; runtime field-type detect; SELECTOR constants
    portal_parse.py   # PURE: parse_due_dates(), select_soonest_due(), extract_prompt_text()
    handoff.py        # make_run_dir(), write_prompt(), render_workflow(), run_session(), read_response()
    errors.py         # typed errors: NotAuthenticated, NoUpcomingDiscussion, SelectorMiss, FillVerifyFailed, EmptyResponse
  templates/
    workflow-CLAUDE.md  # the primed reason→draft→edit workflow for the session
  launcher/
    discuss.desktop     # freedesktop entry
    launch.sh           # opens a terminal running `discuss`
  fixtures/             # saved REAL HTML captured live: discussions_list.html, discussion_page.html, reply_form.html
  tests/
    conftest.py
    test_config.py
    test_portal_parse.py   # against fixtures/
    test_handoff.py
    test_cli_pipeline.py    # adapter mocked
  docs/
    SELECTOR-CAPTURE.md     # operator checklist: capture live selectors + verify live steps
```

## 3. Open Questions Deferred

| ID | Question | Placeholder | Resolved By |
|----|----------|-------------|-------------|
| Q1 | Exact UOPX selectors for class→discussions click-path, prompt container, and reply field | Captured live, then written into `portal_adapter.py` SELECTOR constants | T002 (selector-capture, live) |
| Q2 | Reply-field type — plain textarea vs rich-text/contenteditable | Detect at runtime; handle both | T012 (US3 fill) |
| Q3 | Due-date string format on the discussions list | Discover from `fixtures/discussions_list.html`; parse in `portal_parse.parse_due_dates()` | T007 (US2 parse) |
| Q4 | A `--wait`-capable GUI editor present on the operator's machine | Default `code --wait`; configurable in `config.py`; documented in operator setup | T004 (config) + T002 setup notes |
| Q5 | The exact `claude` invocation that gets primed by the run-dir `CLAUDE.md` | Launch `claude` with `cwd=run_dir`; the workflow `CLAUDE.md` + `prompt.md` live there | T009 (handoff) + T010 (live session verify) |

## 4. Risks & Assumptions

### Risks
1. **Unknown/changing portal DOM (top risk).** Mitigation: quarantine in `portal_adapter.py`
   (FR-013), capture against the live portal (T002), re-verify via `docs/SELECTOR-CAPTURE.md`.
   Recovery cost: one-file edit + re-run the live checklist.
2. **Rich-text injection doesn't "take"** (contenteditable quirks, framework-managed state).
   Mitigation: verify-by-read-back (FR-012) + abort/preserve/manual-paste fallback.
   Recovery cost: adjust injection strategy inside the adapter; the draft is never lost.
3. **`claude` priming contract** (does cwd `CLAUDE.md` reliably drive the workflow?).
   Mitigation: run in the run dir; validate by a live session run (T010). Recovery cost:
   adjust `handoff.run_session()` (e.g. pass the prompt as an initial argument).
4. **Session expiry mid-run.** Mitigation: login-detection + manual-login pause (FR-003).
   Recovery cost: low — operator logs in, run continues.
5. **Wrong-target selection.** Mitigation: confirmation gate (FR-005). Recovery cost: low —
   operator declines.

### Assumptions
1. Operator is on Linux with a desktop environment and `claude` on PATH.
2. Operator logs into UOPX by hand once in the persistent profile; the session persists.
3. The discussions view lists a parseable due date per discussion.
4. Prompt content is plaintext once the discussion page is reached.

## 5. Parallelization Strategy

- **Phase 1 (Setup)** and **Phase 2 (Foundational: `config`, `handoff` scaffolding,
  `errors`, persistent-browser skeleton)** block everything; do first.
- After foundations, **US1 (reason-and-draft engine)** and **US2 (discover+extract)** are
  largely independent and can proceed in parallel — US1 touches `handoff`/`templates`, US2
  touches `portal_parse`/`portal_adapter`. Their tests (`test_handoff.py`,
  `test_portal_parse.py`) are independent.
- **US3 (fill)** depends on the browser/adapter foundations (shares `portal_adapter.py`
  with US2 but different methods).
- **US4 (one-click wiring)** depends on US1–US3 and is the integration slice.
- The **live tasks** (T002 selector-capture, T010 live-session verify, T013 live-fill
  verify, T015 end-to-end) are operator/verification tasks and serialize against access to
  the real portal — they are coordination items, not parallelizable build work.

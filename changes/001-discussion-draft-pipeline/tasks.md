---
name: tasks
purpose: Executable task breakdown
author: design agent
phase: tasks
---

# Tasks: `discussion-draft-pipeline`

**Status:** v1
**Date:** 2026-06-01
**Companion to:** `spec.md` and `plan.md`

**Input**: `changes/001-discussion-draft-pipeline/{spec.md, plan.md}`.

**Prerequisites**: spec.md ✓, plan.md ✓.

**Organization**: tasks are grouped by user story so each story can be implemented and
tested independently. Pure logic is TDD; live-portal and prompt-artifact work is
explicitly marked **[LIVE]** — it is a coordination/verification item executed against the
real portal (its oracle is the operator checklist in `docs/SELECTOR-CAPTURE.md`), **not**
pre-codeable build work, because the UOPX DOM is unknown until inspected (spec §3.3).

## Format

- Task headers: `### T<id> [markers] [depends: …] — description`.
- Markers: `[P]` parallelizable · `[TDD]` RED-GREEN-REFACTOR · `[REVIEW]` G2 before
  consumers · `[no-review]` skips G2 (trivially mechanical / artifact / coverage-exempt) ·
  `[LIVE]` validated against the real portal via operator checklist (no automatable
  oracle) · `[US1..]` story · `[SETUP]/[FOUND]/[POLISH]` phase.
- `**Files touched:**` lists exact paths.

## G2 firing rule

G2 fires at a task checkpoint **iff** the task touches production code **outside** the
Constitution §1 coverage-exempt globs (`src/discuss/browser.py`,
`src/discuss/portal_adapter.py`, `launcher/**`, `templates/**`) **and** is not
`[no-review]`. So `portal_adapter.py` / `browser.py` / launcher / template tasks never
fire G2 (they are exempt and live-verified); `config.py`, `portal_parse.py`, `handoff.py`,
`cli.py` tasks do.

---

## Phase 1 — Setup (shared infrastructure)

### T001 [SETUP] [no-review] — Project skeleton & packaging

**Files touched:** Create `pyproject.toml`, `src/discuss/__init__.py`,
`src/discuss/cli.py` (stub), `tests/conftest.py`, `.gitignore`.

**Expected behavior (FR-001):** An installable package exposing a `discuss` console
script (entry `discuss.cli:main`), with Playwright + a pure-HTML parser (`selectolax`) +
pytest declared. `discuss --help` runs (even if the pipeline is a stub).

- [x] **T001**
  - `pyproject.toml`: project name `discuss`, `requires-python = ">=3.11"`,
    dependencies `["playwright", "selectolax"]`, dev extra `["pytest", "pytest-cov"]`,
    `[project.scripts] discuss = "discuss.cli:main"`, src layout (`packages = ["discuss"]`,
    `package-dir = {"" = "src"}`).
  - `src/discuss/__init__.py`: `__version__ = "0.1.0"`.
  - `src/discuss/cli.py` (stub): `def main(): print("discuss"); return 0`.
  - `.gitignore`: `__pycache__/`, `*.pyc`, `.pytest_cache/`, `profile/`, `runs/`,
    `htmlcov/`, `.coverage`.

### Tests
- (setup/scaffold) covered downstream; smoke: `pip install -e .[dev]` then `discuss --help`
  exits 0.

**Acceptance criterion:** `pip install -e .[dev]` succeeds and `discuss` is on PATH.

---

## Phase 2 — Foundational (blocking prerequisites)

> **⚠️ CRITICAL**: no user-story work begins until this phase completes. T002 (live
> capture) blocks every task that needs real selectors or fixtures.

### T002 [SETUP] [LIVE] [no-review] — Capture live selectors, fixtures & operator setup

**Files touched:** Create `fixtures/login_page.html`,
`fixtures/discussions_list.html`, `fixtures/discussion_page.html`,
`fixtures/reply_form.html`; create `docs/SELECTOR-CAPTURE.md`; seed
`src/discuss/portal_adapter.py` SELECTOR constants (values filled from capture).

**Expected behavior (FR-013, spec §3.3):** Against the **live, logged-in** UOPX portal,
the operator captures the real markup and records the real selectors for: the class
button, the discussions list (rows + due-date cells), a discussion prompt container, and
the reply field. Saved HTML is committed as fixtures for parsing tests. This is a
coordination/verification item — its oracle is the checklist, not a unit test.

- [x] **T002**
  - Install browsers: `python -m playwright install chromium`.
  - Open the persistent profile once. Save the **logged-out login page** first, then log
    in by hand and save the discussions-list page, one discussion page, and the reply-form
    page — four fixtures total (use `page.content()` or browser "Save As → HTML").
  - Record each selector + the due-date string format in `docs/SELECTOR-CAPTURE.md`, and
    write them into `portal_adapter.py` `SELECTORS = {...}` constants.
  - `docs/SELECTOR-CAPTURE.md` doubles as the **re-verification checklist** (run it after
    any portal change): navigated correctly? extracted the right prompt? filled field
    shows the text? did NOT submit?

### Tests
- **[LIVE] oracle:** operator checklist in `docs/SELECTOR-CAPTURE.md` — all four checks
  pass against the live portal.
- **Non-goals for testing:** no automated test hits the live portal (Constitution §2, P-I).

```ears
The tool SHALL confine every portal-specific selector to a single adapter module. [test: test_selectors_confined_to_adapter]
```

**Acceptance criterion:** Three real fixtures committed; `SELECTORS` populated; the
checklist exists and has been run once green by the operator.

---

### T003 [FOUND] [no-review] — Typed errors

**Files touched:** Create `src/discuss/errors.py`.

**Expected behavior (FR-014):** One exception class per fail-loud condition so the
orchestrator can report the specific failing step.

- [x] **T003**

```python
# src/discuss/errors.py
class DiscussError(Exception):
    """Base for all fail-loud conditions. Carries an operator-facing message."""

class NotAuthenticated(DiscussError): ...
class NoUpcomingDiscussion(DiscussError): ...
class SelectorMiss(DiscussError): ...
class EmptyResponse(DiscussError): ...
class FillVerifyFailed(DiscussError): ...
```

### Tests
- (trivial/mechanical) covered by consumers (`test_cli_pipeline.py` asserts the right
  subclass is raised per condition).

**Acceptance criterion:** Module imports; each error subclasses `DiscussError`.

---

### T004 [FOUND] [TDD] — Configuration

**Files touched:** Create `src/discuss/config.py`, `tests/test_config.py`.

**Expected behavior (FR-005, Q4):** A `Config` resolving: `profile_dir` (persistent
browser profile), `target_classes` (list of class identifiers), `confirm` (bool, default
**True**), `editor_cmd` (list, default `["code", "--wait"]`), `run_root` (where run dirs
live). Values come from a config file / env with documented defaults; `confirm` defaults
on.

- [x] **T004 — RED → GREEN → REFACTOR**
  - RED: write the failing tests below; watch them fail (`Config` undefined).
  - GREEN: implement `Config.load(overrides: dict | None = None)` returning a dataclass
    with the defaults; env/file overrides merged over defaults.
  - REFACTOR: keep defaults in one place; no duplicated literals.

### Tests
```python
# tests/test_config.py
from discuss.config import Config

def test_confirm_defaults_on():
    # FR-005: the wrong-target safety gate is on unless explicitly disabled.
    assert Config.load({}).confirm is True

def test_editor_default_is_wait_capable():
    # FR-009: save+close must block, so the default editor carries --wait.
    assert Config.load({}).editor_cmd == ["code", "--wait"]

def test_overrides_win():
    # operator config overrides defaults.
    c = Config.load({"confirm": False, "editor_cmd": ["gedit"]})
    assert c.confirm is False and c.editor_cmd == ["gedit"]
```
- **Edge cases:** empty overrides → all defaults; unknown keys ignored (not crash).
- **Non-goals for testing:** reading any real OS config path (use injected overrides).

```ears
WHERE the operator has not disabled it, the tool SHALL enable the confirmation gate by default. [test: test_confirm_defaults_on]
```

**Acceptance criterion:** `Config.load({})` returns the documented defaults; overrides win.

---

### T005 [FOUND] [TDD] — Run-dir & file handoff I/O

**Files touched:** Create `src/discuss/handoff.py`, `tests/test_handoff.py`. Modify
`templates/` (a tiny test template is fine; the real one is T007).

**Expected behavior (FR-006, FR-007, FR-015):** Filesystem handoff primitives:
`make_run_dir(run_root) -> Path` (unique per run); `write_prompt(run_dir, prompt_text,
meta) -> Path` (writes `prompt.md`); `render_workflow(run_dir, template_path)` (copies the
workflow into `run_dir/CLAUDE.md`); `read_response(run_dir) -> str` (reads `response.md`,
raises `EmptyResponse` if missing/whitespace-only).

- [x] **T005 — RED → GREEN → REFACTOR**
  - RED: write the tests below against a `tmp_path`; watch them fail.
  - GREEN: implement the four functions; `read_response` strips and raises
    `EmptyResponse` on empty/whitespace.
  - REFACTOR: single source for the filenames (`PROMPT_FILE = "prompt.md"`, etc.).

### Tests
```python
# tests/test_handoff.py
import pytest
from discuss import handoff
from discuss.errors import EmptyResponse

def test_write_prompt_creates_prompt_md(tmp_path):
    # FR-006: extracted prompt lands in the run dir.
    rd = handoff.make_run_dir(tmp_path)
    p = handoff.write_prompt(rd, "Discuss X.", {"title": "Wk1", "due": "2026-06-08"})
    assert p.name == "prompt.md" and "Discuss X." in p.read_text()

def test_read_response_returns_saved_text(tmp_path):
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("My edited answer.\n")
    assert handoff.read_response(rd) == "My edited answer."

def test_read_response_empty_raises(tmp_path):
    # FR-012/FR-014: an empty draft must not be treated as a valid response.
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("   \n")
    with pytest.raises(EmptyResponse):
        handoff.read_response(rd)
```
- **Edge cases:** missing `response.md` → `EmptyResponse`; run dirs are unique across calls.
- **Non-goals for testing:** launching `claude` (that's T008).

```ears
IF the saved response is missing or whitespace-only, THEN the tool SHALL raise rather than proceed to write-back. [test: test_read_response_empty_raises]
```

**Acceptance criterion:** All three tests pass; filenames defined once.

---

### T006 [FOUND] [no-review] [depends: T002] — Persistent browser context & auth predicate

**Files touched:** Create `src/discuss/browser.py` (coverage-exempt); add the pure
`is_login_page` predicate to `src/discuss/portal_parse.py`, with its tests in
`tests/test_portal_parse.py` (no separate test file).

**Expected behavior (FR-002, FR-003):** `open_persistent_context(profile_dir) ->
(context, page)` using `launch_persistent_context` (no credentials stored). A pure
predicate `is_login_page(url: str, html: str) -> bool` (placed in `portal_parse.py` so it
is testable) decides whether the current page is the login screen; `browser.ensure_logged_in(page)`
uses it to **pause and prompt** the operator on the login page (FR-003), never automating
credentials.

- [x] **T006**
  - `open_persistent_context`: live/exempt — wraps Playwright; verified in T009/T019.
  - Factor `is_login_page(url, html)` into `portal_parse.py` and TDD it against
    `fixtures/` (a saved login page if captured in T002, else a recorded URL marker).
  - `ensure_logged_in(page)`: loops at human pace — print "Please log in, then press
    Enter", wait for operator, re-check predicate; raise `NotAuthenticated` only if the
    operator gives up. **No** tight polling (P-I).

### Tests
```python
# tests/test_portal_parse.py (auth predicate portion)
from discuss.portal_parse import is_login_page

def test_login_page_detected_by_marker(login_fixture_html, login_url):
    # FR-003: recognise the login screen so we can pause for manual login.
    assert is_login_page(login_url, login_fixture_html) is True

def test_authenticated_page_not_login(discussions_fixture_html, discussions_url):
    assert is_login_page(discussions_url, discussions_fixture_html) is False
```
- **[LIVE] portion:** `open_persistent_context` + the pause UX verified in T019.
- **Non-goals:** automating the login form (forbidden — FR-003).

```ears
IF the operator is not authenticated when a run starts, THEN the tool SHALL pause and prompt for manual login before proceeding. [no-oracle]
```

**Acceptance criterion:** `is_login_page` tests pass; `ensure_logged_in` pauses (verified
live in T019); no credential is ever read or written.

---

## Phase 3 — User Story 1 — Reason-and-draft engine (Priority: P1) 🎯 MVP

**Goal**: A primed session turns a prompt into an operator-edited `response.md`.
**Independent Test**: Drop a sample `prompt.md` in a run dir, run the session, complete
dialogue + GUI edit, confirm `response.md` reflects the operator's input. No browser.

### T007 [US1] [LIVE] [no-review] [depends: T005] — Author the workflow `CLAUDE.md`

**Files touched:** Create `templates/workflow-CLAUDE.md` (coverage-exempt artifact).

**Expected behavior (FR-007, FR-008, FR-009):** The primed workflow instructs the session
to: (1) read `prompt.md`; (2) surface the prompt's key angles/tensions; (3) ask the
operator their stance, main points, and any reading/evidence — and **wait** for answers
(must not auto-generate without input); (4) draft a response grounded in those answers
into `response.md`; (5) open the draft in the configured GUI editor via a **blocking**
command (e.g. `code --wait response.md`) and wait for save+close; (6) confirm "ready to
insert? [y]" then exit. It explicitly forbids submitting anything and frames the work as
assisting the operator's own post (P-II).

- [x] **T007** — write `templates/workflow-CLAUDE.md` per the steps above; reference
  `prompt.md` and `response.md` by name; embed the editor-open + block step; state the
  no-auto-generate and no-submit rules.

### Tests
- **[LIVE] oracle:** T009 run-through (a behavioral prompt; judged by the session's
  actual behavior, not coverage).

```ears
The session SHALL draw out the operator's stance and evidence and ground the draft in that input before opening the editor. [no-oracle]
```

**Acceptance criterion:** Template exists and encodes steps 1–6, the no-auto-generate
rule, and the no-submit rule.

---

### T008 [US1] [TDD] [depends: T005] — `handoff.run_session()`

**Files touched:** Modify `src/discuss/handoff.py`; modify `tests/test_handoff.py`.

**Expected behavior (FR-007):** `run_session(run_dir, editor_cmd) -> str` renders the
workflow into the run dir, launches `claude` **interactively with `cwd=run_dir`**
(blocking), and on exit returns `read_response(run_dir)`. The editor command is made
available to the session via env (`DISCUSS_EDITOR`) so the workflow can open it. Subprocess
is mocked in tests; the live behavior is T009.

- [x] **T008 — RED → GREEN → REFACTOR**
  - RED: test that `run_session` invokes the claude subprocess with `cwd=run_dir` and the
    editor in env, then returns the response text (subprocess + `read_response` exercised
    via a written `response.md`).
  - GREEN: implement using `subprocess.run`; pass `env={**os.environ,
    "DISCUSS_EDITOR": " ".join(editor_cmd)}`.
  - REFACTOR: keep the command/env construction in one helper.

### Tests
```python
# tests/test_handoff.py
import subprocess
from discuss import handoff

def test_run_session_invokes_claude_in_run_dir(tmp_path, monkeypatch):
    rd = handoff.make_run_dir(tmp_path)
    (rd / "response.md").write_text("final text")
    calls = {}
    def fake_run(cmd, cwd=None, env=None, **kw):
        calls.update(cmd=cmd, cwd=cwd, env=env)
        class R: returncode = 0
        return R()
    monkeypatch.setattr(subprocess, "run", fake_run)
    out = handoff.run_session(rd, ["code", "--wait"])
    assert calls["cwd"] == rd
    assert calls["cmd"][0] == "claude"
    assert calls["env"]["DISCUSS_EDITOR"] == "code --wait"
    assert out == "final text"
```
- **Edge cases:** non-zero claude exit → raise (run aborted); empty response → `EmptyResponse`.
- **Non-goals:** the interactive dialogue/editor behavior (live, T009).

```ears
WHEN the session subprocess exits successfully, the tool SHALL return the saved response from the run dir. [test: test_run_session_invokes_claude_in_run_dir]
```

**Acceptance criterion:** Test passes; `claude` launched with `cwd=run_dir` and editor in env.

---

### T009 [US1] [LIVE] [no-review] [depends: T007, T008] — Live session verification

**Files touched:** Append a "US1 session" checklist section to `docs/SELECTOR-CAPTURE.md`.

**Expected behavior (FR-008, FR-009):** A real run with a sample `prompt.md` confirms the
session asks for the operator's input before drafting, opens the GUI editor and blocks,
and that the edited `response.md` reflects the operator's edits.

- [x] **T009** — run `handoff.run_session` against a sample prompt; verify dialogue →
  draft → editor blocks → edited `response.md`. Record pass/fail in the checklist.

### Tests
- **[LIVE] oracle:** checklist — input solicited before draft? editor blocked until close?
  response.md = edited text?

```ears
WHEN the primed session completes with a saved edited draft, the tool SHALL treat the saved file as the final response. [no-oracle]
```

**Acceptance criterion:** Checklist run green once.

**Checkpoint**: US1 is independently usable (manual prompt-in, edited response-out).

---

## Phase 4 — User Story 2 — Auto-discover & extract (Priority: P2)

**Goal**: From the logged-in portal, select the soonest-due discussion and extract its
prompt. **Independent Test**: see spec US2.

### T010 [US2] [TDD] [P] [depends: T002] — Parse due dates & select soonest-due

**Files touched:** Create `src/discuss/portal_parse.py` (parsing portion); create
`tests/test_portal_parse.py`.

**Expected behavior (FR-004):** Pure functions on HTML strings —
`parse_discussions(html) -> list[Discussion]` (each `title, due_date|None, url`) and
`select_soonest_due(items, today) -> Discussion | None`: nearest **future** due date;
skips past-due and unparseable dates; deterministic tiebreak (earliest due, then list
order); returns `None` when nothing is upcoming.

- [x] **T010 — RED → GREEN → REFACTOR**
  - RED: write the tests below against `fixtures/discussions_list.html`; watch them fail.
  - GREEN: parse with `selectolax`; parse the due-date format recorded in T002; implement
    selection.
  - REFACTOR: separate parsing from selection; one date-format constant.

### Tests
```python
# tests/test_portal_parse.py
import datetime as dt
from discuss.portal_parse import parse_discussions, select_soonest_due

def test_select_soonest_due_from_fixture(discussions_fixture_html):
    # FR-004: pick the nearest FUTURE due date.
    items = parse_discussions(discussions_fixture_html)
    chosen = select_soonest_due(items, today=dt.date(2026, 6, 1))
    assert chosen.due_date == min(i.due_date for i in items if i.due_date and i.due_date >= dt.date(2026, 6, 1))

def test_no_upcoming_due_returns_none():
    # FR-014 edge: all past → no target.
    items = [type("D", (), {"title": "old", "due_date": dt.date(2020, 1, 1), "url": "u"})()]
    assert select_soonest_due(items, today=dt.date(2026, 6, 1)) is None

def test_unparseable_due_skipped():
    items = [
        type("D", (), {"title": "bad", "due_date": None, "url": "a"})(),
        type("D", (), {"title": "good", "due_date": dt.date(2026, 6, 8), "url": "b"})(),
    ]
    assert select_soonest_due(items, today=dt.date(2026, 6, 1)).title == "good"
```
- **Edge cases:** tie on due date → earliest-then-list-order; empty list → `None`.
- **Non-goals:** live navigation (T012).

```ears
WHEN the operator triggers a run and is authenticated, the tool SHALL select the discussion with the soonest upcoming due date. [test: test_select_soonest_due_from_fixture]
IF no discussion has an upcoming due date, THEN the tool SHALL stop and report rather than select a past or arbitrary discussion. [test: test_no_upcoming_due_returns_none]
```

**Acceptance criterion:** All selection tests pass against the real fixture.

---

### T011 [US2] [TDD] [P] [depends: T002] — Extract prompt text

**Files touched:** Modify `src/discuss/portal_parse.py`; modify `tests/test_portal_parse.py`.

**Expected behavior (FR-006):** `extract_prompt_text(html) -> str` returns the plaintext
prompt from a discussion page, normalized (collapsed whitespace, no markup).

- [x] **T011 — RED → GREEN → REFACTOR**
  - RED: assert extracted text equals the known prompt in `fixtures/discussion_page.html`.
  - GREEN: select the prompt container (selector from T002), return its text.
  - REFACTOR: shared normalization helper.

### Tests
```python
# tests/test_portal_parse.py
from discuss.portal_parse import extract_prompt_text

def test_extract_prompt_text_from_fixture(discussion_page_fixture_html):
    text = extract_prompt_text(discussion_page_fixture_html)
    assert "expected known prompt sentence" in text  # exact substring from the captured fixture
    assert "<" not in text  # markup stripped
```
- **Edge cases:** empty container → empty string (caller treats as failure).
- **Non-goals:** live extraction (T012).

```ears
WHEN the discussion page is loaded, the tool SHALL return its prompt as normalized plaintext. [test: test_extract_prompt_text_from_fixture]
```

**Acceptance criterion:** Extracted text matches the fixture's known prompt.

---

### T012 [US2] [LIVE] [no-review] [depends: T010, T011, T006] — Live navigate & extract

**Files touched:** Modify `src/discuss/portal_adapter.py` (coverage-exempt); create
`tests/test_selector_confinement.py`.

**Expected behavior (FR-004, FR-006, FR-016):** Adapter methods using the captured
selectors + `portal_parse`: `go_to_discussions(page, class_id)`, `list_discussions(page)
-> [Discussion]` (delegates to `parse_discussions`), `open_discussion(page, disc)`,
`extract_prompt(page) -> str` (delegates to `extract_prompt_text`). Human-paced; minimum
page loads; raises `SelectorMiss` naming the step on any missing selector.

- [x] **T012** — implement against captured selectors; verify live (checklist T013).

### Tests
```python
# tests/test_selector_confinement.py
import pathlib

def test_selectors_confined_to_adapter():
    # FR-013/SC-002: portal selectors live ONLY in the adapter module.
    src = pathlib.Path("src/discuss")
    offenders = [p.name for p in src.glob("*.py")
                 if p.name != "portal_adapter.py" and "SELECTORS" in p.read_text()]
    assert offenders == []
```
- **Unit:** `test_selectors_confined_to_adapter` — falsifiable: adding `SELECTORS` to any
  non-adapter module reds it (FR-013/SC-002). Runs without the live portal.
- **[LIVE] oracle:** T013 checklist (lands on soonest-due; extracted text matches page).
- **Non-goals for testing:** no automated live hit (parsing already covered by T010/T011).

```ears
WHILE a run is in progress, the tool SHALL act at human pace and SHALL NOT issue automated retry loops against the portal. [no-oracle]
The tool SHALL define portal selectors only in the single adapter module. [test: test_selectors_confined_to_adapter]
```

**Acceptance criterion:** Adapter wired to selectors + parse; raises `SelectorMiss` loudly.

---

### T013 [US2] [LIVE] [no-review] [depends: T012] — Live discover+extract verification

**Files touched:** Append "US2 discover/extract" checklist to `docs/SELECTOR-CAPTURE.md`.

**Expected behavior:** Real run lands on the soonest-due discussion and extracts the
correct prompt; confirmation gate names the right discussion + due date.

- [x] **T013** — run live; verify selection + extraction + gate naming. Record result.

### Tests
- **[LIVE] oracle:** checklist.

**Acceptance criterion:** Checklist run green; selected discussion = soonest upcoming due.

**Checkpoint**: US2 feeds US1 automatically.

---

## Phase 5 — User Story 3 — Fill the reply form, no submit (Priority: P3)

**Goal**: Inject the final response into the reply field and verify, never submitting.

### T014 [US3] [TDD] [P] — Read-back verification (pure)

**Files touched:** Modify `src/discuss/portal_parse.py`; modify `tests/test_portal_parse.py`.

**Expected behavior (FR-012, P-IV):** `verify_fill_readback(intended: str, actual: str) ->
bool` — normalizes whitespace/newlines on both sides and compares; the decision is pure so
it is unit-tested independent of the live field.

- [x] **T014 — RED → GREEN → REFACTOR**
  - RED: tests below fail (`verify_fill_readback` undefined).
  - GREEN: normalize (strip, collapse internal whitespace, unify newlines) then `==`.
  - REFACTOR: reuse the normalization helper from T011.

### Tests
```python
# tests/test_portal_parse.py
from discuss.portal_parse import verify_fill_readback

def test_readback_match_ignores_trailing_ws():
    assert verify_fill_readback("My answer.", "My answer.\n") is True

def test_readback_mismatch_detected():
    # FR-012: a partial/garbled paste must fail verification.
    assert verify_fill_readback("My full answer.", "My full") is False
```
- **Edge cases:** empty intended → False; rich-text adds `<p>` wrappers → compare on text.
- **Non-goals:** live injection (T015).

```ears
IF the read-back does not equal the intended text, THEN the tool SHALL report the fill as failed. [test: test_readback_mismatch_detected]
```

**Acceptance criterion:** Both tests pass.

---

### T015 [US3] [LIVE] [no-review] [depends: T002, T014] — `fill_reply()` with runtime type detection

**Files touched:** Modify `src/discuss/portal_adapter.py` (coverage-exempt).

**Expected behavior (FR-010, FR-011, FR-012):** `fill_reply(page, text) -> None`:
1. Locate the reply field via captured selectors; if absent → `SelectorMiss`.
2. **Detect type at runtime**: textarea → `fill()`; contenteditable/rich-text → focus and
   type/`insert_text` into the editable body (handle iframe if the editor is framed).
3. Read the rendered content back; call `verify_fill_readback`; on `False` →
   `FillVerifyFailed`.
4. **Never** locate or click a submit/post control. On any raise, the caller preserves
   `response.md` and instructs manual paste.

- [x] **T015** — implement; the no-submit guarantee and read-back are verified live (T016).

### Tests
- **[LIVE] oracle:** T016 checklist (rendered field equals response; nothing submitted).
- **Non-goals for testing:** the read-back decision is already unit-tested (T014); no live
  automated test.

```ears
WHEN filling the reply, the tool SHALL detect the field type at runtime and SHALL NOT submit the post. [no-oracle]
IF the reply field cannot be located, THEN the tool SHALL raise rather than guess. [no-oracle]
```

**Acceptance criterion:** Fill handles both field types; no submit control is ever invoked;
raises on miss/mismatch.

---

### T016 [US3] [LIVE] [no-review] [depends: T015] — Live fill verification

**Files touched:** Append "US3 fill" checklist to `docs/SELECTOR-CAPTURE.md`.

**Expected behavior:** Real run fills the field; rendered content equals the response; the
post is **not** submitted; an artificially undetectable field aborts write-back and
preserves `response.md`.

- [x] **T016** — verify all three live; record result.

### Tests
- **[LIVE] oracle:** checklist.

**Acceptance criterion:** Field shows the response, unsubmitted; abort path preserves the file.

**Checkpoint**: US3 closes the loop on the back end.

---

## Phase 6 — User Story 4 — One-click end-to-end (Priority: P4)

**Goal**: Wire the full pipeline behind the launcher.

### T017 [US4] [TDD] [REVIEW] [depends: T004, T005, T008, T010, T011, T014] — Orchestrator pipeline

**Files touched:** Modify `src/discuss/cli.py`; create `tests/test_cli_pipeline.py`.

**Expected behavior (FR-001, FR-005, FR-010, FR-012, FR-014, FR-015):** `run(config,
browser_factory, adapter, today)` orchestrates: open context → `ensure_logged_in` →
`adapter.go_to_discussions` → `list_discussions` → `select_soonest_due` (None →
`NoUpcomingDiscussion`, stop) → **confirmation gate** (decline → abort, no extraction) →
`extract_prompt` → `write_prompt` → `run_session` (→ `response.md`) → **persist confirmed**
→ `fill_reply` → on `FillVerifyFailed`/`SelectorMiss`: keep `response.md`, print manual-paste
message → report discussion title. The **adapter and session are injected** so the pipeline
is fully testable with fakes; live wiring is T019.

- [x] **T017 — RED → GREEN → REFACTOR**
  - RED: write the tests below with a `FakeAdapter` (records calls, configurable to raise)
    and a stubbed `run_session`; watch them fail.
  - GREEN: implement the orchestration with the ordering guarantees.
  - REFACTOR: each step a small named function; the order reads top-to-bottom.

### Tests
```python
# tests/test_cli_pipeline.py
import datetime as dt
import pytest
from discuss import cli
from discuss.errors import NoUpcomingDiscussion, FillVerifyFailed

def test_confirm_decline_aborts(fake_ctx):
    # FR-005: declining the gate extracts nothing and fills nothing.
    fake_ctx.confirm_answer = False
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.extracted is False
    assert fake_ctx.adapter.filled is False

def test_confirm_gate_names_discussion(fake_ctx):
    # FR-005: the confirmation gate names the selected discussion and its due date.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.selected.title in fake_ctx.gate_prompt
    assert str(fake_ctx.selected.due_date) in fake_ctx.gate_prompt

def test_no_upcoming_due_stops(fake_ctx):
    # FR-014: nothing upcoming → stop, no fill.
    fake_ctx.adapter.discussions = []  # select_soonest_due → None
    with pytest.raises(NoUpcomingDiscussion):
        cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.filled is False

def test_extracted_prompt_written(fake_ctx):
    # FR-006: confirmed run writes prompt.md before the session.
    cli.run(**fake_ctx.kwargs)
    assert (fake_ctx.run_dir / "prompt.md").exists()

def test_response_persisted_before_fill(fake_ctx):
    # FR-015: response.md exists on disk before fill is attempted.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.response_existed_at_fill is True

def test_fill_does_not_submit(fake_ctx):
    # FR-010: the happy path fills but never submits.
    cli.run(**fake_ctx.kwargs)
    assert fake_ctx.adapter.filled is True
    assert fake_ctx.adapter.submitted is False

def test_fill_verify_mismatch_aborts(fake_ctx):
    # FR-012: a failed read-back aborts write-back, preserves the response, AND tells the
    # operator to paste manually — assert all three limbs of the criterion.
    fake_ctx.adapter.fill_raises = FillVerifyFailed("read-back mismatch")
    cli.run(**fake_ctx.kwargs)
    assert (fake_ctx.run_dir / "response.md").exists()       # preserved
    assert fake_ctx.adapter.submitted is False               # aborted: never submitted
    assert "paste" in fake_ctx.last_message.lower()          # manual-paste instruction
```
- **Edge cases:** `NotAuthenticated` surfaces from `ensure_logged_in`; `SelectorMiss`
  mid-pipeline preserves any response and reports the step.
- **Non-goals:** live browser/session (T019).
- **Fixtures:** `fake_ctx` builds a `FakeAdapter` (flags: `extracted`, `filled`,
  `submitted`, `response_existed_at_fill`, `fill_raises`, `discussions`), exposes
  `selected` (the chosen discussion), and captures the confirmation `gate_prompt` and the
  operator-facing `last_message` reported by `cli.run`; plus a stub `run_session` writing a
  non-empty `response.md`, and the `kwargs` for `cli.run`.

```ears
WHEN the operator declines the confirmation gate, the tool SHALL abort the run without extracting anything. [test: test_confirm_decline_aborts]
WHEN a discussion is selected, the tool SHALL present a confirmation naming the discussion and its due date. [test: test_confirm_gate_names_discussion]
WHEN the operator confirms the gate, the tool SHALL write the extracted plaintext prompt to the run dir. [test: test_extracted_prompt_written]
IF no discussion has an upcoming due date, THEN the tool SHALL stop and report. [test: test_no_upcoming_due_stops]
WHEN the session completes, the tool SHALL fill the reply without submitting it. [test: test_fill_does_not_submit]
IF the read-back does not equal the intended text, THEN the tool SHALL abort write-back and preserve the response file. [test: test_fill_verify_mismatch_aborts]
The tool SHALL persist the final response to disk before attempting write-back. [test: test_response_persisted_before_fill]
```

**Acceptance criterion:** All pipeline tests pass; **[REVIEW] gate (G2)** fires (production
code in `cli.py`).

**Checkpoint**: Full pipeline runs end-to-end with fakes.

---

### T018 [US4] [no-review] [depends: T001] — Desktop launcher

**Files touched:** Create `launcher/discuss.desktop`, `launcher/launch.sh` (coverage-exempt).

**Expected behavior (FR-001):** `launch.sh` opens a terminal emulator running `discuss`;
`discuss.desktop` is a freedesktop entry pointing at `launch.sh` with an icon/name, so a
double-click starts a run.

- [x] **T018** — write `launch.sh` (detect a terminal: `x-terminal-emulator`/`gnome-terminal`,
  fallback documented) and `discuss.desktop` (`Type=Application`, `Exec=…/launch.sh`,
  `Terminal=false`, `Name=Discuss`).

### Tests
- (artifact) smoke: `desktop-file-validate launcher/discuss.desktop` passes; `bash -n
  launcher/launch.sh` parses.

**Acceptance criterion:** `.desktop` validates; clicking it (verified in T019) starts a run.

---

### T019 [US4] [LIVE] [no-review] [depends: T012, T015, T017, T018, T006] — End-to-end live verification

**Files touched:** Append "US4 end-to-end" + "login-pause" checklist to `docs/SELECTOR-CAPTURE.md`.

**Expected behavior (FR-001, FR-003, SC-001, SC-003):** Clicking the launcher runs the full
pipeline to a filled, unsubmitted reply on the soonest-due discussion; a logged-out start
pauses for manual login then continues; confirm no credential is written and no submit
occurs.

- [x] **T019** — run the full flow live (logged in, and logged out); record results.

### Tests
- **[LIVE] oracle:** checklist (SC-001 end state; SC-003 no-submit/no-creds; FR-003 pause).

```ears
WHEN the operator clicks the launcher while authenticated, the tool SHALL run the full pipeline to a filled, unsubmitted reply on the soonest-due discussion. [no-oracle]
```

**Acceptance criterion:** End-to-end checklist green; login-pause path works.

**Checkpoint**: SC-001 achieved end-to-end.

---

## Phase 7 — Polish & cross-cutting

### T020 [POLISH] [P] [no-review] — README & operator setup docs

**Files touched:** Create `README.md`; finalize `docs/SELECTOR-CAPTURE.md`.

**Expected behavior:** README covers install (`pip install -e .[dev]`, `playwright
install chromium`), first-login into the profile, editor config, the launcher, and the
re-verify-after-portal-change procedure. Restates the no-submit / no-creds / respectful-use
guarantees.

- [x] **T020** — write the docs.

### Tests
- **Aggregate:** `pytest` green; non-exempt coverage meets Constitution §1 (line 85 /
  branch 75); `desktop-file-validate` green.

**Acceptance criterion:** A new operator can set up and run from the README alone.

---

## Dependencies & execution order

- **Setup (T001)** → start immediately.
- **T002 (live capture)** → blocks every fixture/selector consumer (T006, T010–T016).
- **Foundational (T003–T006)** → block all stories.
- **US1 (T007–T009)** and **US2 parsing (T010, T011)** → parallel after foundations.
- **US2 live (T012, T013)** → after T010/T011 + T002.
- **US3 (T014–T016)** → T014 parallel; T015/T016 after T002 + T014.
- **US4 (T017–T019)** → T017 after the pure units; T018 after T001; T019 after all live + T017.
- **Polish (T020)** → last.

Within each story: tests RED-first before implementation; respect every `[depends: …]`;
commit after each task whose tests pass (and after G2 clears for `[REVIEW]` tasks).
**[LIVE]** tasks serialize against real-portal access and are verification/coordination
items — their oracle is `docs/SELECTOR-CAPTURE.md`, not pytest.

## Review Log

> Append-only. Execute appends one row per gate verdict (G2/G3). Empty until execution.

| Gate | Anchor | Verdict | Key findings |
|------|--------|---------|--------------|
| G1 | spec.md + plan.md + tasks.md | clear (+ no-oracle residue) | testability / completeness-consistency / scope all PASS after 2 design bounces. Fixed: selector-confinement made testable (was `[no-oracle]`), multi-limb fill-mismatch now asserts all three limbs, stale plan task-id refs (§3/§4/§5), bidirectional file-map gaps (cli.py, test_selector_confinement.py, dangling test_auth_predicate.py), login-page fixture added. **Residue (FR-015):** the live-portal + interactive-session criteria are `[no-oracle]` and verified by the operator checklist in `docs/SELECTOR-CAPTURE.md` during execute — not by automated tests. |
| G2 | T004 (confirm-gate-default EARS; config defaults) | clear | spec-match: `test_confirm_defaults_on` criterion satisfied (`confirm: bool = True`, `load({})` constructs with no override). quality: PASS — no defects; mutable-default handling (default_factory for list fields, Path immutables) verified correct, no injection via `cls(**kwargs)` (known-field filter). 100% line/branch coverage on config.py. |
| G2 | T005 (missing/blank-response-raises EARS; handoff I/O) | clear | spec-match: `test_read_response_empty_raises` satisfied — `read_response` strips then raises `EmptyResponse` on blank AND missing before any write-back. quality: PASS — no leaks (self-closing I/O), explicit utf-8, `mkdtemp` collision-free; benign exists()→read TOCTOU and None-input both non-defects under tool-controlled single-operator threat model. 100% line/branch on handoff.py. |
| G2 | T008 (session-exit-returns-response EARS; run_session) | clear | spec-match: `test_run_session_invokes_claude_in_run_dir` satisfied — `run_session` launches `claude` (`cmd[0]`) with `cwd=run_dir` + `DISCUSS_EDITOR` env, returns `read_response` on rc==0. quality: PASS — list-arg subprocess (no shell=True, no injection), env is superset of `os.environ` (PATH/HOME preserved), non-zero→DiscussError, blank→EmptyResponse. Noted: `" ".join(editor_cmd)` lossy on space-containing args (operator-config fidelity nit, not a defect; matches task GREEN). 100% line/branch on handoff.py. |
| G2 | T014 (read-back-mismatch-fails EARS; verify_fill_readback) | BLOCK→clear (1 bounce) | quality BLOCK (round 1): symmetric tag-strip stripped markup from the *intended* side too → fail-OPEN (`verify("Use Vec<String>","Use Vec<HashMap>")` wrongly True), letting a garbled paste pass the FR-012 safety gate. **Fix:** asymmetric normalization — `intended` whitespace-collapsed only (literal `<…>` preserved), `actual` markup-stripped; added regression tests (incl. empty-actual). Round 2: quality PASS (fail-open gone; tag-strip on actual can only delete spans, residual ambiguity fails SAFE) + spec-match PASS (`test_readback_mismatch_detected`). 100% line/branch on portal_parse.py. |
| G2 | T010 (soonest-due + no-upcoming-stop EARS; parse_discussions/select_soonest_due) | BLOCK→clear (1 bounce) | spec-match PASS: `test_select_soonest_due_from_fixture` (picks 2026-06-02 Wk1, the soonest upcoming) + `test_no_upcoming_due_returns_none` (all-past → None) both satisfied. quality BLOCK (round 1): `PROMPT_CONTAINER_SEL` imported into portal_parse.py but unused (it belongs to T011's extractor) — F401 dead import. **Fix:** removed the import (returns with T011). Round 2: quality PASS — no dead imports, strptime guarded by try/except ValueError (bad/empty cells → None, no crash), stable-`min` tie-break deterministic, no injection/leak surface. **Capture correction:** `discussion_rows` selector changed `makeStylescontainer`→`makeStylescontentListItem` so each row nests its own due-date cell (the recorded one excluded them, making every discussion look undated); verified 7 rows/5 dated against the fixture. 100% line/branch on portal_parse.py. |
| G2 | T011 (prompt-as-normalized-plaintext EARS; extract_prompt_text) | clear | spec-match PASS: `test_extract_prompt_text_from_fixture` satisfied — `css_first` takes the FIRST of the 12 reused `#bb-editor-textbox` containers (the instructor prompt, not a student reply) and returns `collapse_whitespace(node.text(separator=' '))`, markup stripped. quality PASS: re-added `PROMPT_CONTAINER_SEL` now consumed (no dead import); None-guard returns "" on absent container (no crash); pure in-memory selectolax parse, no injection/leak/perf hazard; `collapse_whitespace` correct over already-markup-free `node.text()`. 100% line/branch on portal_parse.py. |
| G2 | T006 ([no-review] — skipped) | n/a | G2 does not fire: the codeable slice is the pure `is_login_page` predicate (in portal_parse.py, 100% line/branch — marker-in-body with /login-URL fallback, 3 tests incl. authenticated-page-not-login and url-only path) and `browser.py` is coverage-exempt (live Playwright). **No-oracle residue (FR-015):** the `ensure_logged_in` manual-login pause is `[no-oracle]`, verified by the operator login-pause checklist in T019 — never read or typed a credential. |
| G2 | T012 ([no-review] — skipped) | n/a | G2 does not fire: adapter nav/extract methods (`go_to_discussions`/`list_discussions`/`open_discussion`/`extract_prompt`) are coverage-exempt live Playwright (delegate parsing to the unit-tested portal_parse; raise `SelectorMiss` naming the step; lazy portal_parse import avoids the constants cycle). Codeable unit `test_selectors_confined_to_adapter` PASSES and is **proven falsifiable** (injecting `SELECTORS` into cli.py reds it, revert greens it) — FR-013/SC-002. **No-oracle residue (FR-015):** human-paced/no-retry-loop + live land-on-soonest/extract are `[no-oracle]`, verified in T013. |
| G2 | T015 ([no-review] — skipped) | n/a | G2 does not fire: `fill_reply` is coverage-exempt live Playwright. Runtime type detect (textarea/input→`fill()`+`input_value()`; contenteditable Quill→focus/clear/`insert_text`+`inner_text()`; neither→`FillVerifyFailed` abort); `SelectorMiss` if field absent (raise, never guess, FR-011); read-back checked by the **unit-tested** pure `verify_fill_readback` (T014), `FillVerifyFailed` on mismatch. **No-submit guarantee is structural** — verified by grep that the function contains no submit/post-control lookup or click (the only `.click()` focuses the editable field). **No-oracle residue (FR-015):** runtime-detect/no-submit + rendered-equals-response + undetectable-field-aborts are `[no-oracle]`, verified in T016. |
| G2 | T017 (orchestrator: 7 EARS — decline/gate-names/prompt-written/no-upcoming/no-submit/mismatch-abort/persist-before-fill; cli.run) | clear | spec-match PASS: all 7 criteria satisfied, each multi-limb criterion confirmed to assert every limb (gate names title+due; mismatch asserts abort+preserve+manual-paste; no-upcoming stop limb + report limb via `test_main_reports_discuss_error`). quality PASS: confirm gate un-bypassable (`config.confirm and not confirm`), persist-response precedes fill, only narrow named excepts (`FillVerifyFailed`/`SelectorMiss` at fill, `DiscussError` in main), no unused imports / mutable-default / broad-except. Reviewer noted `_context` is never closed — **by design** (browser is left open with the unsubmitted draft for the operator to review+submit, P-II); added a clarifying comment. 100% line/branch on cli.py; 50/50 suite green. |
| G2 | T020 ([no-review] — skipped) | n/a | G2 does not fire (docs). README.md authored (install / first-login / editor / launcher / re-verify / principles + the no-submit/no-creds/no-auto-generate guarantees); `docs/SELECTOR-CAPTURE.md` status finalized (capture done). **Aggregate floor green:** 50/50 pytest; every non-exempt module 100% line/branch (cli, config, errors, handoff, portal_parse) — exceeds Constitution §1 (85/75); `desktop-file-validate` PASS; `bash -n launch.sh` OK. |
| G2 | T017-fix (cli.main config gathering; FR-001/FR-005/FR-014) | clear | **Bug found running live:** `main()` called `Config.load()` with no overrides, so `target_classes==[]` crashed at `target_classes[0]` with `IndexError` (config.py had delegated env/file gathering to cli.py, which never did it). **Fix:** added `_load_overrides(env)` reading `DISCUSS_TARGET_CLASSES`/`DISCUSS_EDITOR`/`DISCUSS_PROFILE_DIR`/`DISCUSS_RUN_ROOT`/`DISCUSS_CONFIRM`, and a fail-loud guard (print guidance + return 2) when no class is configured. spec-match PASS (env→config→run reached; no-class→non-zero+guidance, run never reached). quality PASS (live `os.environ` default reads current env per call — verified by setenv tests; malformed `","`/whitespace classes route to fail-loud, empirically confirmed; no mutable-default/dead code). 100% line/branch on cli.py; 53/53 suite. README documents the env vars. |
| G3-residue | T009/T013/T016/T019 ([LIVE] [no-oracle]) | **OPERATOR-WAIVED — NOT verified live** | The four story-level live verifications were **waived by the operator (2026-06-02), not executed**. These are the FR-015 `[no-oracle]` residue (oracle = the live checklist in `docs/SELECTOR-CAPTURE.md`, against the real logged-in portal). They were **not** run; do **not** read these checkboxes as "verified live". **Residual risk accepted by operator:** the no-submit guarantee (FR-010) and no-credentials-stored (FR-002) are confirmed only by code inspection + fake-based unit tests (T014/T015/T017 + the structural no-submit grep), NOT against the live Blackboard Ultra reply form; likewise the login-pause (FR-003), live soonest-due selection/extraction (T013), and end-to-end flow (T019) are unconfirmed on the real portal. If a live selector or the runtime field-type detection is wrong, these behaviors are unverified. Re-run §3 + the story checklists in `docs/SELECTOR-CAPTURE.md` before relying on the tool against the live portal. |

---
name: tasks
purpose: Executable task breakdown
author: design agent
phase: tasks
---

# Tasks: `discussion-draft-pipeline`

**Status:** v2 (post-Escalation #2: Phase 9 added)
**Date:** 2026-06-02
**Companion to:** `spec.md` and `plan.md`

**Input**: `changes/001-discussion-draft-pipeline/{spec.md, plan.md}`.

**Prerequisites**: spec.md ✓, plan.md ✓.

**Organization**: tasks are grouped by user story so each story can be implemented and
tested independently. Pure logic is TDD; live-portal and prompt-artifact work is
explicitly marked **[LIVE]** — it is a coordination/verification item executed against the
real portal, **not** pre-codeable build work, because the UOPX DOM is unknown until
inspected (spec §3.3).

> ## ⛳ Escalation #1 re-triage (2026-06-02) — task-state & oracle changes
>
> The first build reached "done / all-green" while the program could not run and its
> safety guarantees were unverified (see `## Escalation #1` at the end of this file). The
> corrective restructure:
>
> 1. **`[x]` no longer means "verified" for live tasks.** The four story-level live
>    checks (old **T009 / T013 / T016 / T019**) were *operator-waived, not run* — so their
>    boxes are flipped back to **`[ ] DEFERRED — live-unverified`** below. Their
>    offline-verifiable substance moves to the new agent oracles **T021–T025**; their one
>    irreducibly-live residue consolidates into the single guided run **T026**.
> 2. **New state — DEFERRED.** A `[LIVE]` validation that has not been run renders as
>    `[ ] DEFERRED — live-unverified`, **never** `[x]`. A change carrying any DEFERRED
>    safety check is **PROVISIONAL**, not done (SC-007). US1 (no portal) still reaches
>    genuine *done* on its own.
> 3. **New oracles (all agent work — zero operator burden):** Phase 8 (**T021–T025**)
>    adds the structural no-submit / no-creds oracles, the `file://` fill oracle against
>    the captured Quill form, the no-mock entry-point smoke gate, and the guided
>    `discuss validate` flow. The operator does *nothing* for these.
> 4. **The only human step is smooth (T026).** The retired `docs/SELECTOR-CAPTURE.md`
>    ordeal (paste a throwaway script, juggle stale tabs, hand-record selectors, walk four
>    checklists) is replaced by **one** `discuss validate` run: log in once, press a key at
>    each checkpoint. The tool self-snapshots the DOM on a selector miss (FR-018).

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
IF the operator is not authenticated when a run starts, THEN the tool SHALL pause and prompt for manual login before proceeding. [test: test_ensure_logged_in_pauses_on_login_page]
```

**Acceptance criterion:** `is_login_page` tests pass; `ensure_logged_in` pause **logic** is
verified offline in **T027** (`test_ensure_logged_in_pauses_on_login_page`), the live
confirmation folding into T026; no credential is ever read or written.

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

- [ ] **T009 — DEFERRED (live-unverified)** — was operator-waived, not run (Escalation #1).
  The live session run-through now happens inside the single guided run **T026**; nothing
  here renders as done. (US1's offline substance — `run_session` — is `[x]` done at T008.)

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
WHILE a run is in progress, the tool SHALL act at human pace and SHALL NOT issue an automated retry loop on a selector miss. [test: test_no_retry_loop_on_selector_miss]
The tool SHALL define portal selectors only in the single adapter module. [test: test_selectors_confined_to_adapter]
```

**Acceptance criterion:** Adapter wired to selectors + parse; raises `SelectorMiss` loudly.

---

### T013 [US2] [LIVE] [no-review] [depends: T012] — Live discover+extract verification

**Files touched:** Append "US2 discover/extract" checklist to `docs/SELECTOR-CAPTURE.md`.

**Expected behavior:** Real run lands on the soonest-due discussion and extracts the
correct prompt; confirmation gate names the right discussion + due date.

- [ ] **T013 — DEFERRED (live-unverified)** — was operator-waived, not run (Escalation #1).
  Live discover/extract/gate now happens inside the single guided run **T026**.

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

- [ ] **T016 — DEFERRED (live-unverified)** — was operator-waived, not run (Escalation #1).
  The offline substance (real `fill_reply` vs the captured Quill form; no-submit) is now
  **automatable** — see **T021** (structural no-submit) and **T022** (`file://` fill
  oracle). The irreducibly-live confirmation folds into the guided run **T026**.

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

- [ ] **T019 — DEFERRED (live-unverified)** — was operator-waived, not run (Escalation #1).
  End-to-end + login-pause is the single guided run **T026**; the seam that actually
  crashed live is now gated offline by the no-mock smoke test **T024**.

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

## Phase 8 — Escalation #1 correctives (oracle hardening + smooth validation)

> **All of T021–T025 are agent work — the operator does nothing.** They convert the
> previously waivable safety residue into automatable offline oracles. **T026** is the one
> irreducible human-in-the-loop run, and it is deliberately smooth (log in once, press a
> key). This phase is what makes "all green" mean the program *runs* and its safety
> guarantees *hold* — the two things Escalation #1 proved the old gate set did not certify.

### T021 [P] [no-review] — Structural no-submit oracle (FR-010, SC-007)

**Files touched:** Create `tests/test_no_submit.py`.

**Expected behavior:** A test reads the *source* of `portal_adapter.fill_reply`
(`inspect.getsource`) and asserts it contains **no** submit/post-control lookup or click —
the only `.click()` focuses the editable field. Proves the safety *absence* on every
build, offline. Falsifiable: injecting a post-button `.click()` reds it; reverting greens
it.

- [x] **T021** — wrote `tests/test_no_submit.py`; passes against the current adapter and
  proven falsifiable (injected `page.query_selector("[type='submit']").click()` → RED;
  reverted → GREEN, adapter byte-identical).

### Tests
```python
# tests/test_no_submit.py
import ast, inspect
from discuss import portal_adapter

def _code_without_docstring(fn) -> str:
    """The function as code with its docstring removed and comments dropped, so the oracle
    scans CODE — not the prose that legitimately documents the no-submit guarantee. (The
    earlier `"submit" in getsource` form false-RED'd on the docstring; G1 caught it.)"""
    node = ast.parse(inspect.getsource(fn)).body[0]
    body = node.body
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)):
        node.body = body[1:]                       # drop the docstring statement
    return ast.unparse(node).lower()               # ast.unparse omits comments entirely

def test_fill_reply_has_no_submit_path():
    # FR-010/SC-007: the fill CODE may not look up or click a submit/post control.
    code = _code_without_docstring(portal_adapter.fill_reply)
    for forbidden in ("submit", "post-button", "btn_post", "publish", "[type='submit']"):
        assert forbidden not in code, f"fill_reply CODE references {forbidden!r}"
    assert code.count(".click(") <= 1              # the only click focuses the editable field
```

```ears
The reply-fill code path SHALL contain no submit/post-control lookup or click. [test: test_fill_reply_has_no_submit_path]
```

**Acceptance criterion:** Test passes; proven falsifiable (add a post click → red; revert → green).

---

### T022 [TDD] [P] [depends: T015] — `file://` fill oracle against the captured Quill form (FR-011, FR-012)

**Files touched:** Create `tests/test_fill_offline.py`; adjust `src/discuss/portal_adapter.py`
(coverage-exempt) **only if** the real path fails the fixture.

**Expected behavior:** Drive the **real** `portal_adapter.fill_reply` against
`fixtures/reply_form.html` loaded via `file://` in a headless Chromium — the controlled
real boundary (Constitution §2). Assert: runtime type-detection picks the contenteditable
Quill branch (not hard-coded), the editor renders the injected text, `verify_fill_readback`
passes, and **nothing is submitted** (no navigation occurs; URL stays the `file://` fixture).
This exercises the actual fill surface the criterion names — not a fake.

- **RED:** write the test; it fails until `fill_reply` correctly handles the captured
  Quill markup (if the captured selector/branch is wrong, this is where it surfaces —
  offline, with zero submit risk, instead of live).
- **GREEN/REFACTOR:** fix `fill_reply` in the exempt adapter if needed.
- **No silent skips:** if `playwright install chromium` is absent the test must `skip`
  with a loud printed reason — never pass silently (no-silent-caps; the skip is visible).

- [x] **T022 — RED → GREEN → REFACTOR** — wrote `tests/test_fill_offline.py`; the **real**
  `fill_reply` drives the captured Quill `reply_form.html` over `file://` in headless
  Chromium (ran 3.6s, not skipped) and renders the text, passes read-back, navigates
  nothing. **No adapter fix needed** — the captured contenteditable branch works as-is.
  Proven falsifiable: neutering the `insert_text` → RED (`FillVerifyFailed` caught the empty
  field); a non-matching `REPLY_FIELD_SEL` → RED (`SelectorMiss`); revert → GREEN.

### Tests
```python
# tests/test_fill_offline.py
import pathlib, pytest
from discuss import portal_adapter

playwright = pytest.importorskip("playwright.sync_api",
    reason="LOUD SKIP: `playwright install chromium` not present — file:// fill oracle not run")

def test_fill_against_captured_reply_form():
    from playwright.sync_api import sync_playwright
    fixture = pathlib.Path("fixtures/reply_form.html").resolve().as_uri()
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(); page.goto(fixture)
        start_url = page.url
        portal_adapter.fill_reply(page, "My drafted reply.")   # real adapter, real DOM
        field = page.query_selector(portal_adapter.REPLY_FIELD_SEL)
        assert "My drafted reply." in field.inner_text()        # rendered effect, not return value
        assert page.url == start_url                            # nothing navigated/submitted
        b.close()
```

```ears
WHEN filling the captured reply form offline via file://, the tool SHALL detect the field type at runtime, fill it, pass read-back, and submit nothing. [test: test_fill_against_captured_reply_form]
```

**Acceptance criterion:** The real `fill_reply` passes against the captured Quill fixture
(or the adapter is fixed until it does); the skip path is loud, never silent.

---

### T023 [P] [no-review] — Structural no-credentials oracle (FR-002, SC-007)

**Files touched:** Create `tests/test_no_creds.py`.

**Expected behavior:** A test scans the `src/discuss` tree and asserts no module writes a
credential or fills a login form: the only persistent-state path is the profile dir handed
to `launch_persistent_context`. Proves no-creds offline, every build. Falsifiable: adding
a `page.fill("#password", …)` or writing a secrets file reds it.

- [x] **T023** — wrote `tests/test_no_creds.py`; passes against the current tree and proven
  falsifiable (injected `page.fill('#password', 'hunter2')` into `browser.py` → RED; revert
  → GREEN, `browser.py` byte-identical).

### Tests
```python
# tests/test_no_creds.py
import ast, pathlib

SRC = pathlib.Path("src/discuss")

def _code_only(py: pathlib.Path) -> str:
    """Module source as code: docstrings stripped, comments dropped (ast.unparse) — so the
    safety prose that mentions 'password'/'credential' cannot false-RED this oracle (G1
    caught the earlier bare-word form red-ing on the 'no password field' comment)."""
    tree = ast.parse(py.read_text())
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(body, list) and body and isinstance(body[0], ast.Expr)
                and isinstance(getattr(body[0], "value", None), ast.Constant)
                and isinstance(body[0].value.value, str)):
            node.body = body[1:]                   # drop this scope's docstring
    return ast.unparse(tree).lower()

def test_no_credentials_persisted():
    # FR-002/SC-007: never automate the login form, never store a credential. Scan CODE only,
    # and only for ACTIONABLE patterns (an API call / a real selector / a secrets file) — not
    # the bare words that appear in the modules' safety comments.
    code = "\n".join(_code_only(p) for p in SRC.glob("*.py"))
    for forbidden in ("getpass", "keyring", "#password", "secret=", "credentials.json",
                      "password_field", "login_form", ".fill(pw"):
        assert forbidden not in code, f"a module's CODE references {forbidden!r}"
    # the only persistence is the operator's own browser profile (no stored secret)
    assert "launch_persistent_context" in (SRC / "browser.py").read_text()
```

```ears
The tool SHALL write no portal credential to disk and SHALL touch only the persistent profile directory for session state. [test: test_no_credentials_persisted]
```

**Acceptance criterion:** Test passes; proven falsifiable.

---

### T024 [TDD] [REVIEW] [depends: T017] — No-mock entry-point smoke gate (SC-006, FR-001)

**Files touched:** Create `tests/test_main_smoke.py`; minimal `src/discuss/cli.py` refactor
only if needed for testability (keep `main`/`run` wiring intact).

**Expected behavior:** Drive the **real** entry-point wiring — `Config.load(_load_overrides())
→ run(...)` — to a **defined** state, stubbing **only** `browser_factory` at the outermost
boundary. This is the layer Escalation #1 lacked: the fatal `IndexError` lived in the
`Config.load → run` seam the orchestrator fakes replaced. No fake of any internal seam.

- **RED:** test fails (or would have caught the `IndexError`) before the wiring is sound.
- **GREEN:** real `main()`/`run` reach a defined state.

- [x] **T024 — RED → GREEN → REFACTOR** — wrote `tests/test_main_smoke.py`; **no `cli.py`
  refactor needed** (the seam was already sound post-`f233e72`, so the test locks the
  regression). RED proof, tied to the exact Escalation #1 failure modes: dropping the
  no-class guard in `main()` → `IndexError` at `cli.py:93` (`config.target_classes[0]`,
  literally the bug) → RED; dropping the no-upcoming guard in `run()` →
  `AttributeError: NoneType.title` (seam no longer reaches a defined state) → RED; revert →
  GREEN, `cli.py` byte-identical. **[REVIEW] G2 = clear** (see Review Log).

### Tests
```python
# tests/test_main_smoke.py — only the live browser boundary is stubbed; the rest is REAL.
import datetime as dt
import pytest
from discuss import cli
from discuss.errors import NoUpcomingDiscussion

class _FakePage:  # an outermost-boundary stub: a logged-in portal with no discussions
    def content(self): return "<html></html>"
def _stub_browser_factory(): return (object(), _FakePage())

def test_main_smoke_reaches_defined_state(monkeypatch, tmp_path):
    # SC-006: with a valid config + only the browser stubbed, REAL Config.load→run reaches a
    # DEFINED state (NoUpcomingDiscussion), proving the seam is wired — not an IndexError.
    monkeypatch.setenv("DISCUSS_TARGET_CLASSES", "_577963_1")
    monkeypatch.setenv("DISCUSS_RUN_ROOT", str(tmp_path))
    from discuss.config import Config
    cfg = Config.load(cli._load_overrides())                    # REAL config gathering
    class _A:                                                    # adapter at the live boundary
        def go_to_discussions(self, page, cid): pass
        def list_discussions(self, page): return []             # → select_soonest_due None
    with pytest.raises(NoUpcomingDiscussion):
        cli.run(config=cfg, browser_factory=_stub_browser_factory, adapter=_A(),
                today=dt.date(2026, 6, 1), ensure_logged_in=lambda p: None)

def test_main_no_class_exits_with_guidance(monkeypatch, capsys):
    # the guard that the original IndexError needed: real main(), no class → rc 2 + guidance.
    monkeypatch.delenv("DISCUSS_TARGET_CLASSES", raising=False)
    assert cli.main() == 2
    assert "DISCUSS_TARGET_CLASSES" in capsys.readouterr().out
```

```ears
WHEN discuss is invoked with a valid configuration, the tool SHALL reach a defined pipeline state through the real entry-point wiring and SHALL NOT crash in the integration seam. [test: test_main_smoke_reaches_defined_state]
```

**Acceptance criterion:** Both tests pass driving the REAL wiring; **[REVIEW] (G2)** confirms
only the outermost browser boundary is stubbed (no internal-seam fake). `cli.py` is
non-exempt production code, so G2 fires.

---

### T025 [TDD] [REVIEW] [depends: T017, T012, T015, T006] — `discuss validate` guided live-check (FR-017, FR-018)

**Files touched:** Modify `src/discuss/cli.py` (add a `validate` subcommand + arg dispatch
in `main`); create `tests/test_validate.py`.

**Expected behavior (FR-017/FR-018):** `discuss validate` opens the persistent context,
`ensure_logged_in` (pausing if needed), then walks navigate → select → extract → fill,
**narrating each step** and gating each visual checkpoint on a **single-keypress** confirm
(reusing the `confirm` seam): e.g. "Found ‹title› due ‹date› — correct? [y]", "Filled the
reply field — your text shows, nothing submitted? [y]". On any `SelectorMiss`, it snapshots
`page.content()` to `fixtures/<step>_live.html` itself (FR-018) and stops, naming
`portal_adapter.py` as the one-file fix — the operator never hand-captures markup. It never
submits. The **flow logic** (single-keypress prompts; decline aborts; miss → snapshot+stop)
is unit-tested with a fake page + fake input + tmp fixtures dir.

- **RED → GREEN → REFACTOR:** drive the dispatch + flow with the tests below.

- [x] **T025 — RED → GREEN → REFACTOR** — added `cli.validate` (the guided walk: per-step
  drive + `[y]`-shaped single-keypress confirm reusing the `_confirm_via_input` seam;
  decline aborts; `SelectorMiss` → self-snapshot `fixtures_dir/<step>_live.html` naming
  `portal_adapter.py`, rc 3; never submits), `cli._run_validate` (live wrapper: fail-loud rc
  2 with no class *before* opening a browser; else open persistent context → `ensure_logged_in`
  → walk), and a `validate` subcommand dispatch in `main(argv=None)` (exact-match, pytest-safe).
  RED first (11 fail: `validate`/`_run_validate` absent), then GREEN. **G2 = clear** (spec-match
  + quality both PASS). Hardened the one minor footgun the quality reviewer flagged — a
  `SelectorMiss` into a missing fixtures dir raised `FileNotFoundError` (defeating FR-018's
  self-capture); added `snapshot.parent.mkdir(parents=True, exist_ok=True)` + a falsifiability-
  proven test (revert the mkdir → that test REDs with the exact `FileNotFoundError`). cli.py
  100% line + 100% branch; 70/70.

### Tests
```python
# tests/test_validate.py
from discuss import cli

def test_guided_validation_uses_single_keypress_confirms(monkeypatch, tmp_path):
    # FR-017: every checkpoint is a single-keypress confirm; declining stops the walk.
    prompts = []
    def fake_confirm(p): prompts.append(p); return True
    cli.validate(fake_page_factory(), adapter=FakeAdapter(), confirm=fake_confirm,
                 fixtures_dir=tmp_path)
    assert prompts, "validate must ask the operator to confirm at least one checkpoint"
    assert all("[y]" in p.lower() for p in prompts)              # single-keypress shape

def test_validate_snapshots_dom_on_selector_miss(monkeypatch, tmp_path):
    # FR-018: a selector miss self-snapshots the live DOM; operator never hand-captures.
    cli.validate(fake_page_factory(miss_at="extract"), adapter=FakeAdapter(miss="extract"),
                 confirm=lambda p: True, fixtures_dir=tmp_path)
    assert list(tmp_path.glob("*_live.html")), "a selector miss must snapshot the DOM"
```
- **Fixtures:** `fake_page_factory` / `FakeAdapter` model a page whose `content()` is
  capturable and an adapter configurable to raise `SelectorMiss` at a named step.

```ears
WHEN the operator runs guided validation, the tool SHALL drive each live check itself and gate it on a single-keypress operator confirmation. [test: test_guided_validation_uses_single_keypress_confirms]
```

**Acceptance criterion:** `discuss validate` walks the live steps with single-keypress
confirms and self-snapshots on miss; flow logic green; **[REVIEW] (G2)** fires (`cli.py`).

---

### T027 [TDD] [P] [no-review] [depends: T006, T012] — Pause-logic & no-retry offline oracles (FR-003, FR-016)

**Files touched:** Create `tests/test_adapter_logic.py`; adjust `src/discuss/browser.py`
(coverage-exempt) only if `ensure_logged_in` needs a give-up signal to be testable.

**Expected behavior:** Two offline oracles for behavior the old plan wrongly left
`[no-oracle]` — both tested against **fakes**, no live portal, so two more safety/pace
criteria stop being waivable:

1. **Login-pause logic (FR-003):** a fake page whose url/html reads as the login screen
   (`is_login_page → True`) makes `browser.ensure_logged_in` **prompt and pause** for
   manual login (never auto-filling a credential), and raise `NotAuthenticated` only when
   the operator gives up. Asserts the pause *happens* — the live page-recognition residue
   stays in T026.
2. **No-retry (FR-016 / P-I):** a fake page whose row query returns `None` makes
   `portal_adapter.go_to_discussions` raise `SelectorMiss` after **exactly one**
   navigation (no retry loop).

- **RED → GREEN → REFACTOR:** drive both with the tests below. If `ensure_logged_in` loops
  unboundedly, add a give-up signal (e.g. the operator typing `q`) so the pause is
  testable while staying human-paced by default.

- [x] **T027 — RED → GREEN → REFACTOR** — wrote `tests/test_adapter_logic.py`. No-retry
  oracle passed against the current adapter as-is (one `goto`, then `SelectorMiss`). Login-pause
  oracle RED first: the old `wait=input` default bound the **real** builtin at def-time, so the
  monkeypatched fake was never used (`OSError: reading from stdin`) and there was no give-up
  path. GREEN: `browser.ensure_logged_in` now resolves `input` **at call time** (`ask = input if
  wait is None else wait`), prompts with a "log in"-bearing message, gives up
  (`NotAuthenticated`) on `q` **or** EOF, and proceeds once authenticated — never auto-fills a
  credential. Added a third oracle (proceeds-once-authenticated) pinning the loop exit.
  `browser.py` is coverage-exempt (no G2); the tests ARE the oracle. 73/73.

### Tests
```python
# tests/test_adapter_logic.py
import pytest
from discuss import browser, portal_adapter
from discuss.errors import NotAuthenticated, SelectorMiss

class _LoginPage:
    url = "https://www.phoenix.edu/login"
    def content(self): return "<title>University of Phoenix Login</title>"

def test_ensure_logged_in_pauses_on_login_page(monkeypatch):
    # FR-003: a login page makes ensure_logged_in PROMPT/pause; it never auto-fills creds,
    # and gives up (NotAuthenticated) only when the operator declines.
    prompts = []
    monkeypatch.setattr("builtins.input", lambda p="": prompts.append(p) or "q")  # operator quits
    with pytest.raises(NotAuthenticated):
        browser.ensure_logged_in(_LoginPage())
    assert prompts and any("log in" in p.lower() for p in prompts)   # the pause prompt fired

def test_no_retry_loop_on_selector_miss():
    # FR-016/P-I: a selector miss raises after exactly ONE navigation — no retry storm.
    gotos = []
    class _Page:
        def goto(self, url, **kw): gotos.append(url)
        def query_selector(self, sel): return None      # rows never resolve
    with pytest.raises(SelectorMiss):
        portal_adapter.go_to_discussions(_Page(), "_577963_1")
    assert len(gotos) == 1, "go_to_discussions must not retry-loop on a selector miss"
```
- **Non-goals:** the *live* login page recognition + live navigation (those are T026).

```ears
IF the operator is not authenticated when a run starts, THEN the tool SHALL pause and prompt for manual login before proceeding. [test: test_ensure_logged_in_pauses_on_login_page]
WHILE a run is in progress, the tool SHALL NOT issue an automated retry loop on a selector miss. [test: test_no_retry_loop_on_selector_miss]
```

**Acceptance criterion:** Both offline oracles pass against fakes; the login-pause and
no-retry criteria (formerly `[no-oracle]`) are now automatable. `browser.py`/`portal_adapter.py`
are coverage-exempt, so G2 does not fire (the tests are the oracle).

---

### T026 [LIVE] [depends: T030] — Single smooth guided validation run (DEFERRED — live-unverified)

**Files touched:** none (this is the one irreducible human-in-the-loop run; it may *produce*
`fixtures/*_live.html` — now post-render, FR-018 — if a selector has drifted).

**Expected behavior (residue of FR-003/FR-004/FR-006/FR-010/FR-011/FR-012; SC-005):** the
operator runs `discuss validate` once against the live portal. Post-Escalation #2 the run
exercises the **redesigned** flow: navigate → **wait for render** → **classify landing**;
if the SSO login shell appears, the tool **pauses for manual login in the same window**
(FR-003), the operator logs in by hand (choosing any *"keep me signed in / trust this
device"* option presented — this seeds the persistence T031 checks), the tool **retries the
navigation once**, then proceeds; the operator presses `y`/`n` at each narrated checkpoint
(found discussion / extracted prompt / filled sample). This validates that the SPA renders
within the bounded wait and that the post-navigation login pause actually fires — the two
things the first live run proved broken. It **replaces** the four retired checklists (old
T009/T013/T016/T019). Passing it (with T031) flips the change PROVISIONAL → live-verified.

- [ ] **T026 — DEFERRED (live-unverified).** Not a build task; the agent MUST NOT check
  this box. Its oracle is the operator's single-keypress confirmations during the guided
  run — render-timing and the live login redirect are irreducibly live (the classification
  *decision* and auth *sequencing* are already offline-tested by T028/T029). If the operator
  defers it, the tool ships honestly labeled **"code-verified, live-unverified"**, never
  "done". US1 is independently *done* regardless.

### Tests
- **[LIVE] oracle:** the guided run's per-checkpoint operator confirmations.

```ears
WHEN the operator completes the guided validation run with all checkpoints confirmed, the tool SHALL be recorded live-verified; UNTIL then the change SHALL present as provisional, not done. [no-oracle]
```

**Acceptance criterion:** Either run green by the operator (→ live-verified), or it stands
DEFERRED and the change stays PROVISIONAL — the two states are distinct and neither is "done
while unverified".

---

## Phase 9 — Escalation #2 correctives (SPA-render + auth-flow + persistence)

> **Why this phase.** The first live `discuss validate` proved the deferred live residue's
> *shape* was architectural, not a selector-value swap: a client-rendered SPA read
> pre-render, an SSO redirect the pre-navigation auth check could never see, and a session
> that may not survive a relaunch (forcing re-2FA — operator-unacceptable). T028/T029 are
> **offline** agent work the first pass wrongly assumed was live (the captured pre-render
> shell makes login-classification a real fixture oracle; auth re-sequencing is flow logic
> under the no-mock smoke). T030 is the coverage-exempt live adapter change. **T031** is the
> single new *blocking* live check: a second run must skip re-auth/2FA. The change stays
> PROVISIONAL until T026 **and** T031 pass.

### T028 [TDD] [REVIEW] [depends: T006] — Login-shell classification offline oracle (FR-003, FR-018; Esc#2)

**Files touched:** create `fixtures/login_shell_prerender.html` (copied verbatim from the
captured `changes/001-discussion-draft-pipeline/evidence-navigate_live.html`); extend
`src/discuss/portal_parse.py`; create `tests/test_landing_classify.py`. `portal_parse.py` is
non-exempt → **G2 fires**.

**Expected behavior:** Add a pure `classify_landing(url, html) -> "login" | "discussions" |
"unknown"` and broaden `is_login_page` so the **pre-render** ForgeRock SPA shell is
recognized as a login page. The shell carries none of the post-render
`"University of Phoenix Login"` marker — key instead on its stable pre-render markers
(`<title>Login</title>` **and** `data-testid="fr-body-image"`, plus the IdP/`/login` URL-host
fallback), without false-positiving the real discussions list. `classify_landing` returns
`discussions` when the discussion-rows selector resolves in the markup, `login` on the login
shell, else `unknown`. This is the offline oracle the first pass assumed was live — the
captured shell IS the fixture (Escalation #2 corrective: a captured-on-failure artifact is a
new offline oracle, not just a re-capture target).

- [x] **T028 — RED → GREEN → REFACTOR** — created `fixtures/login_shell_prerender.html`
  (verbatim from the FR-018 evidence snapshot) + `tests/test_landing_classify.py`. RED first:
  `classify_landing` absent (ImportError) and the pre-render shell undetected by the old
  `is_login_page`. GREEN: added `LOGIN_SHELL_TITLE_MARKER`/`LOGIN_SHELL_BODY_MARKER` to the
  adapter (selector home, FR-013) and broadened `is_login_page` (post-render marker OR the
  pre-render title+body markers TOGETHER OR `/login` URL) + new pure `classify_landing`
  (rows-first → `discussions`, else login predicate → `login`, else `unknown`). Proven
  falsifiable (neuter the `LOGIN_SHELL_*` branch → `test_classify_prerender_login_shell` REDs;
  revert → GREEN, byte-identical). 76/76; `portal_parse.py` 100% line+branch. **G2 = clear**
  (spec-match + quality both PASS).

### Tests
- `test_classify_prerender_login_shell` — `classify_landing(url, <login_shell_prerender.html>) == "login"` **and** `is_login_page(url, shell) is True` (the bug the first live run hit).
- `test_classify_discussions_list` — `classify_landing(url, <discussions_list.html>) == "discussions"`.
- `test_classify_unknown_markup` — arbitrary HTML → `"unknown"` (so a real selector miss is still distinguishable from a login redirect).
- existing `test_is_login_page_*` (post-render `login_page.html`) still pass — no regression.

```ears
WHEN a portal navigation lands on the client-rendered login shell, the tool SHALL classify it as a login page from the pre-render markup (not as a selector miss). [test: test_classify_prerender_login_shell]
```

**Acceptance criterion:** Tests pass; falsifiable (revert the predicate change → `test_classify_prerender_login_shell` REDs).

---

### T029 [TDD] [REVIEW] [depends: T028, T017, T024] — Re-sequence auth post-navigation + in-context retry (FR-002, FR-003; Esc#2)

**Files touched:** `src/discuss/cli.py`; extend `tests/test_main_smoke.py` (and/or
`tests/test_auth_sequencing.py`). `cli.py` is non-exempt → **G2 fires**.

**Expected behavior:** Remove the pre-navigation `ensure_logged_in(page)` call on the fresh
`about:blank` page in **both** `run` (cli.py:104) and `_run_validate` (cli.py:218) — it can
never see a post-navigation redirect. Replace with: navigate → wait → `classify_landing`; on
`login`, pause for manual login (FR-003) in the **same** context, then **retry the navigation
once** and re-classify; on `discussions`, proceed; on `unknown`, `SelectorMiss`. The adapter's
`go_to_discussions` raises `NotAuthenticated` (not `SelectorMiss`) on a login landing so the
orchestrator can branch. At most one bounded human-paced retry (FR-014/FR-016 — no storm).

**Smoke (no-mock, extends T024):** drive the real `run`/`_run_validate` wiring with a stubbed
browser whose first navigation lands on a `login` classification and whose retry lands on
`discussions`; assert (a) the manual-login pause was invoked **after** navigation, (b) exactly
one retry occurred, (c) a defined downstream state is reached — only the outermost browser
boundary stubbed, no internal seam faked (the SC-006 discipline).

- [ ] **T029** — RED first (the pre-nav auth check / no-retry path); GREEN after re-sequencing.

### Tests
- `test_auth_pause_is_post_navigation_with_retry` — the pause fires after the first navigation and the navigation is retried exactly once in-context before proceeding; no pre-nav auth check runs.
- `test_login_landing_raises_not_authenticated` — a login classification routes to the pause path, not a `SelectorMiss`.

```ears
WHEN a portal navigation lands on the login page, the tool SHALL pause for manual login after navigation and retry the navigation once in the same context before proceeding, and SHALL NOT run the auth check before the first portal navigation. [test: test_auth_pause_is_post_navigation_with_retry]
```

**Acceptance criterion:** Tests pass; G2 (spec-match + quality) clears; the no-mock smoke gates the new seam.

---

### T030 [LIVE] [no-review] [depends: T028, T029] — Condition-based waiting + post-render snapshot (FR-004, FR-016, FR-018; Esc#2)

**Files touched:** `src/discuss/portal_adapter.py` (coverage-exempt live Playwright → **G2
does not fire**; live-verified by T026/T031).

**Expected behavior:** Across `go_to_discussions` / `open_discussion` / `extract_prompt`,
replace `wait_until="domcontentloaded"` + immediate `query_selector` with
`page.wait_for_selector("<rows> , <login-marker>", timeout=<human-paced, ~20s>)` (an efficient
mutation-observer wait, **not** a tight poll — P-I), then `classify_landing(page.url,
page.content())`: `login` → `NotAuthenticated`; `discussions`/prompt present → proceed; timeout
/`unknown` → `SelectorMiss` naming the step. **FR-018 fix:** the `validate` self-snapshot
(cli.py) now fires *after* the wait, so the captured `<step>_live.html` is post-render, not the
1.6 KB shell. The classification *decision* is offline-pinned (T028); only the *wait timing* is
live.

- [ ] **T030 — DEFERRED for live behavior.** The codeable decision logic it calls is offline
  (T028); the wait timing is verified by the T026/T031 live runs. Agent implements; live
  behavior is not auto-checked.

### Tests
- No new offline test owns the live wait (exempt). The decision it delegates to is covered by T028; the post-render snapshot timing is observed in T026/T031.

```ears
WHEN navigating a portal page, the tool SHALL wait for the rendered content (discussion rows or the login marker) within a bounded human-paced timeout and SHALL NOT read or snapshot the DOM pre-render. [no-oracle]
```

**Acceptance criterion:** Implemented; live render-timing confirmed in T026; no offline regression (T028/T029 still green).

---

### T031 [LIVE] [depends: T026, T030] — Session-persistence (no re-2FA) live validation (FR-002, SC-008; **BLOCKING**) (DEFERRED — live-unverified)

**Files touched:** none (live coordination; may produce post-render `fixtures/*_live.html`).

**Expected behavior (residue of FR-002/SC-008):** In **one** operator sitting, immediately
after a successful T026 run (where the operator chose *"keep me signed in / trust this
device"* at login), the operator runs `discuss validate` a **second** time **without** logging
in. **PASS** iff the second run reaches the discussions list (and a filled sample reply)
**without a fresh manual login and without repeating two-step verification**. **FAIL** iff it
lands back on the SSO login shell — persistence is broken; the operator records the finding and
the change **cannot** reach live-verified. This is the blocking precondition the operator's
2FA constraint created: re-doing 2FA every run is unacceptable.

- [ ] **T031 — DEFERRED (live-unverified), BLOCKING.** Not a build task; the agent MUST NOT
  check this box. On FAIL, the tool-owned persistent-profile model is disproven and the
  contingency (attach to the operator's already-authenticated running browser via CDP) is a
  **new spec-level fork** — re-escalate, do not silently adopt. The change stays PROVISIONAL
  until this PASSes or the operator accepts an alternative auth model.

### Tests
- **[LIVE] oracle:** the second run reaching content without re-auth — observed by the operator. No offline oracle exists (session persistence is irreducibly a property of the live IdP + the real profile across real launches).

```ears
WHEN a subsequent run starts after a prior authenticated run within the session's validity window, the tool SHALL reach the discussions list without a fresh manual login or repeated two-step verification. [no-oracle]
```

**Acceptance criterion:** Either PASS (→ contributes to live-verified with T026) or the change stays PROVISIONAL with the persistence finding recorded; never auto-checked.

---

## Dependencies & execution order

- **Setup (T001)** → start immediately.
- **T002 (live capture)** → blocks every fixture/selector consumer (T006, T010–T016).
- **Foundational (T003–T006)** → block all stories.
- **US1 (T007–T009)** and **US2 parsing (T010, T011)** → parallel after foundations.
- **US2 live (T012, T013)** → after T010/T011 + T002.
- **US3 (T014–T016)** → T014 parallel; T015/T016 after T002 + T014.
- **US4 (T017–T019)** → T017 after the pure units; T018 after T001; T019 superseded → T024/T026.
- **Polish (T020)** → last of the original build.
- **Phase 8 correctives (T021–T027, Escalation #1):** T021/T023 (structural oracles) and
  T022 (`file://` fill oracle) run in parallel after their targets exist (T015); T024
  (no-mock smoke) after T017; T025 (`discuss validate`) after T017/T012/T015/T006; T027
  (pause-logic + no-retry offline oracles) after T006/T012; **T026** is operator-run live
  validation — DEFERRED, gating PROVISIONAL → live-verified, never auto-checked. US1 reaches
  *done* independently of all of Phase 8.
- **Phase 9 correctives (T028–T031, Escalation #2):** **T028** (login-shell classification,
  offline) after T006 — it unblocks the rest. **T029** (auth re-sequencing, offline smoke)
  after T028/T017/T024. **T030** (condition-based waiting in the exempt adapter) after
  T028/T029. **T026** now `[depends: T030]` (the guided run exercises the redesigned flow).
  **T031** (persistence / no-re-2FA, **BLOCKING** live) after T026/T030. The change is
  live-verified only when **both T026 and T031** pass; T031 FAIL re-escalates the auth model.
  T028/T029 are agent work (zero operator burden); T030 is agent work, live-verified later;
  T026+T031 are the single operator sitting (log in once, confirm, re-run once).

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
| G2 | T021 ([no-review] — skipped) | n/a | G2 does not fire (test-only task; `portal_adapter.py` is coverage-exempt). The structural no-submit oracle (`test_no_submit.py`) passes and is **proven falsifiable** (inject a `[type='submit']` click → RED, revert → GREEN). Scans the fill CODE with docstring + comments stripped (`ast.unparse`), so it cannot false-RED on the no-submit prose. Aggregate floor green: 54/54. |
| G2 | T022 (file:// fill oracle; not [REVIEW]) | n/a | G2 does not fire (test-only; the adapter is coverage-exempt and unchanged). The `file://` fill oracle runs the REAL `fill_reply` against the captured Quill DOM in headless Chromium and is **proven falsifiable** (neutered insert → `FillVerifyFailed`; wrong reply selector → `SelectorMiss`; revert → GREEN). This is the no-mock, observed-rendered-effect oracle Escalation #1 lesson #2 demanded — it replaces the waivable live fill checklist (old T016) offline, with zero submit risk. 55/55. |
| G2 | T023 ([no-review] — skipped) | n/a | G2 does not fire (test-only). The structural no-credentials oracle (`test_no_creds.py`) passes and is **proven falsifiable** (inject `page.fill('#password', …)` → RED, revert → GREEN). Scans the whole `src/discuss` tree as CODE (docstrings + comments stripped via `ast.unparse`) for ACTIONABLE patterns only, and asserts the sole persistence path is `launch_persistent_context` (the operator's own profile). 56/56. |
| G2 | T024 (no-mock smoke gate; `WHEN discuss invoked with valid config … SHALL reach a defined pipeline state through the real entry-point wiring`) | clear | Floor green (58/58; all non-exempt modules 100% line; `lint-ears.sh` not vendored in this repo, criterion well-formed + G1-cleared). **spec-match PASS:** the test builds config via the REAL `Config.load(cli._load_overrides())` (only env monkeypatched — the real input path) and calls the REAL `cli.run`, exercising the exact `config.target_classes[0]` IndexError site against a real config and reaching the typed `NoUpcomingDiscussion`; only the outermost browser boundary (`browser_factory`/`adapter`/`ensure_logged_in`) is stubbed — no internal seam faked. `test_main_no_class_exits_with_guidance` drives real `main()` + the guard. **quality PASS:** genuine (not self-referential) oracle; `delenv` makes the no-class test browser-safe (guard returns 2 before any `browser_factory()`); `monkeypatch` auto-undo → no cross-test leak/order-dependence; deterministic (no randomness/network). One info nit (DISCUSS_CONFIRM not delenv'd) — immaterial, raises before the confirm gate. |
| G2 | T025 (`discuss validate` guided check; `WHEN the operator runs guided validation … SHALL drive each live check itself and gate it on a single-keypress operator confirmation`) | clear | Floor green (70/70; cli.py 100% line + 100% branch). **spec-match PASS:** `validate` tool-drives all four live steps (navigate → list/select → open/extract → fill), gates three checkpoints each on a `[y]`-shaped `confirm`, decline stops the walk, `SelectorMiss` self-snapshots `<step>_live.html` naming `portal_adapter.py` (FR-018), nothing submitted; the named test is a genuine oracle. **quality PASS:** `main` dispatch exact-match + pytest-safe; `_run_validate` fails loud rc 2 before opening any browser, then persistent-context + login-pause before walking; tests faithful + order-independent. **One minor `violation` finding (not blocking) — FIXED in-role:** a `SelectorMiss` into an absent fixtures dir raised `FileNotFoundError` (defeating FR-018 self-capture); added `mkdir(parents=True, exist_ok=True)` + a falsifiability-proven test (`test_validate_self_snapshots_even_when_fixtures_dir_absent`). |
| G2 | T027 ([no-review] — skipped) | n/a | G2 does not fire (`browser.py` coverage-exempt; `portal_adapter` unchanged). Two formerly-`[no-oracle]` criteria are now automatable offline oracles. **Login-pause (FR-003)** RED-proven: the old def-time `wait=input` binding made the monkeypatch fake unreachable (`OSError: reading from stdin`) and looped forever; fixed to resolve `input` at call time + a `q`/EOF give-up → `NotAuthenticated`, plus a proceeds-once-authenticated oracle — never auto-fills creds. **No-retry (FR-016)** passed against the current adapter (one `goto`, then `SelectorMiss`; `len(gotos)==1`). 73/73. |
| G3 | whole change's criteria + full suite + invariants (P-I..P-IV) | **clear (code-verified) + human-residue (T026 live)** | Floor green with fresh evidence: 73/73; every non-exempt module 100% line + 100% branch (browser.py/portal_adapter.py §1-exempt); all 22 `[test:]` tags bind to collected tests (0 missing). Full G3 panel (context-starved subagents, builder account withheld) all **PASS**: **spec-match** — every safety-critical criterion (no-submit FR-010, no-creds FR-002, login-pause FR-003, no-retry FR-016, entry-point-runs SC-006, fill FR-011/012, guided-validation FR-017/018) has a real, independently-**falsifiable** automated oracle binding to production code, not a self-referential fake; the irreducibly-live residue (T009/T013/T016/T019/T026) is correctly carried DEFERRED/`no-oracle`, never `[x]`. **regression** — no break from the `main(argv=None)` dispatch, the `ensure_logged_in` rewrite (EOF path preserved, `announce` drop safe — no caller passed it), or the extracted `_NO_CLASS_MESSAGE` (byte-identical, rc unchanged). **invariants** — P-I (no creds, one `goto`, fail-stop), P-II (no submit path; `.click()` only focuses the field; draft left unsubmitted), P-III (selectors only in `portal_adapter.py`; runtime field-type detect), P-IV (read-back via `verify_fill_readback`) all upheld. **quality** — no defects; `subprocess` list-arg (no `shell=True`), run-dir writes scoped, `verify_fill_readback` fails SAFE. **Outcome: the change is CODE-VERIFIED and PROVISIONAL — NOT "done".** The single human-residue (T026 guided live run) is surfaced to the operator, never silently passed (FR-015). |
| G2 | T028 (`WHEN a portal navigation lands on the client-rendered login shell … SHALL classify it as a login page from the pre-render markup`) | clear | Floor green (76/76; `portal_parse.py` 100% line+branch). **spec-match PASS:** `test_classify_prerender_login_shell` is a genuine falsifiable oracle — the verbatim FR-018 shell fixture carries `<title>Login</title>`+`data-testid="fr-body-image"` (post-render marker ABSENT), classified `login` from body markup at a non-`/login` URL (URL fallback bypassed); discussions list → `discussions` (rows-first); arbitrary → `unknown`; no regression to existing `is_login_page` tests. **quality PASS:** both functions guard None/empty; discussions-first ordering verified safe in both directions against the real fixture+selector; the broad `<title>Login</title>` substring is acceptably constrained by the AND-paired ForgeRock body marker and fails toward `unknown` (pause/diagnose), never silently "authenticated". |
| G3-residue | T009/T013/T016/T019 ([LIVE] [no-oracle]) | **OPERATOR-WAIVED — NOT verified live** | The four story-level live verifications were **waived by the operator (2026-06-02), not executed**. These are the FR-015 `[no-oracle]` residue (oracle = the live checklist in `docs/SELECTOR-CAPTURE.md`, against the real logged-in portal). They were **not** run; do **not** read these checkboxes as "verified live". **Residual risk accepted by operator:** the no-submit guarantee (FR-010) and no-credentials-stored (FR-002) are confirmed only by code inspection + fake-based unit tests (T014/T015/T017 + the structural no-submit grep), NOT against the live Blackboard Ultra reply form; likewise the login-pause (FR-003), live soonest-due selection/extraction (T013), and end-to-end flow (T019) are unconfirmed on the real portal. If a live selector or the runtime field-type detection is wrong, these behaviors are unverified. Re-run §3 + the story checklists in `docs/SELECTOR-CAPTURE.md` before relying on the tool against the live portal. |

---

## Escalation #1 — 2026-06-02 02:18

**Trigger:** Assumption failure (the plan/process assumed its verification strategy constituted valid acceptance; it did not)
**Blocked at:** Change-level acceptance — surfaced across T017 (orchestrator), the change close-out (T009/T013/T016/T019 waiver), and T017-fix (the post-"done" IndexError).

### Completed Successfully
- All 16 codeable build tasks + the T017-fix implemented under TDD; every per-task G2 panel (spec-match + quality) cleared; 100% line/branch on all non-exempt modules (cli, config, errors, handoff, portal_parse); 53/53 unit suite green.
- A real defect was caught by the process: the `discussion_rows` capture selector excluded due-date cells (fixed, fixture-verified).
- The live-running IndexError was root-caused and fixed once observed (env config gathering + fail-loud guard).

### What Failed
The acceptance process certified the change **done and all-green while the program could not run at all.** The orchestrator (`cli.run`) was tested entirely with builder-authored fakes (FakeAdapter, stub session, injected `make_run_dir`/`confirm`/`ensure_logged_in`), and `main()` — the actual console entry point — was "tested" by monkeypatching `_load_overrides` and `run`. So the single path that executes on a real `discuss` invocation (`Config.load()` with no overrides → `target_classes == []` → `target_classes[0]`) was never exercised end-to-end. Outcome: G2 spec-match PASS, G2 quality PASS, 100% coverage, lint-ears PASS, full suite green — and the **first** live invocation died with `IndexError` before doing any work. The gates validated the design's consistency with itself, not that the artifact runs; the one bug that mattered lived precisely in the integration seam the fakes papered over.

Independently, the change's most safety-critical criteria — no-submit (FR-010), no-credentials (FR-002), login-pause (FR-003), live selection/extraction/fill — are all `[no-oracle]`, their only oracle being an operator checklist against the live portal. When the operator declined to run them, the change was still marked **done** (boxes checked, logged as "operator-waived"). So "done / all boxes checked / all gates green" was reachable with (a) a non-running program and (b) zero evidence the tool's defining safety guarantees hold. Coverage % and G2 verdicts both read as strong positive signals that were, here, hollow.

### Last Command
```
$ DISCUSS_TARGET_CLASSES unset; discuss
```

### Last Error
```
Traceback (most recent call last):
  File "/home/qqp/projects/discuss/.venv/bin/discuss", line 6, in <module>
    sys.exit(main())
  File "/home/qqp/projects/discuss/src/discuss/cli.py", line 110, in main
    run(
  File "/home/qqp/projects/discuss/src/discuss/cli.py", line 60, in run
    adapter.go_to_discussions(page, config.target_classes[0])
IndexError: list index out of range
```
(Bug since fixed in commit f233e72 — cited here as the evidence that a fatal defect passed every gate, not as an open blocker.)

### Decision Needed
The process let a non-running, safety-unverified change reach "done / all-green." Which corrective(s) should the method adopt? Concretely:
- **(A) Mandatory no-mock entry-point smoke gate.** Require at least one test that invokes the real console entry / `main()` with the real `Config.load`/`_load_overrides`/`run` wiring (only the live browser/portal stubbed at the outermost boundary), so "the program starts and reaches a *defined* state" is gated — not just unit fakes. Should this be a G2 floor item for any task touching an entry point / integration seam?
- **(B) Safety criteria cannot be `[no-oracle]`-waivable.** A criterion encoding a safety guarantee (no-submit, no-creds) must not be markable "done" while its only oracle is an unrun live checklist. Either make the live checklist a *blocking* gate, or require an automatable offline oracle. (Demonstrated feasible: running the real `fill_reply` against the captured `fixtures/reply_form.html` via `file://` exercises selector + runtime type-detect + read-back with zero submit risk — a candidate standing oracle for T016.)
- **(C) "Waived" must not render as "done."** Introduce a distinct task state (deferred / unverified) so a change with unrun `[LIVE]` safety checks cannot present as all-boxes-checked / all-green.
- **(D) Coverage honesty.** Should fake-driven entry-point tests be barred from counting toward the entry seam's coverage, so 100% can't be reported while the real path is unexercised?

Which of A–D (or what else) becomes method/plan policy, and does this change require re-opening the contract / spec acceptance criteria for this feature before it can be legitimately closed?

### Builder's Perspective
I watched every gate go green — spec-match, quality, 100% line-and-branch, lint-ears, the whole suite — and handed it off feeling done; then the operator typed `discuss` and it died on the first real line of work. What unsettles me is that I didn't break any rule to get there: the plan said test the orchestrator with injected fakes, so I did, and `main()` was "covered" by monkeypatching the exact functions whose interaction was broken — the fakes proved the design agreed with itself, not that the thing runs, and the only bug that mattered was hiding in the seam the fakes replaced. I'd also been quietly uneasy checking the `[LIVE]` boxes as "operator-waived," because no-submit and no-creds *are* the whole point of this tool and we have no evidence they hold against the real portal — yet the change still rendered as fully done and green. The load-bearing realization is that in this process "all green" and "all boxes checked" were both attainable for a program that neither ran nor had its safety guarantees verified, which means the green told us almost nothing about the two things that matter most. I kept fixing the symptoms in-role (the selector, then the config crash) when the pattern underneath is that our oracles were either self-referential or waivable.

### Generalizable Lesson

A gate's green certifies only what its oracle actually **observes**. This change reached
"done / all-green" because every oracle for a load-bearing behavior was one of two
worthless shapes: **self-referential** (the system under test replaced by fakes the
author also wrote — so the test confirmed the design agreed with itself, never that the
integrated artifact runs) or **waivable** (a manual checklist the operator could skip
while the task still recorded as `[x]`). The builder's testimony — "'all green' and 'all
boxes checked' were both attainable for a program that neither ran nor had its safety
guarantees verified ... our oracles were either self-referential or waivable" — is this
exactly. It is the constitution's own **P-IV (observed effect ≠ reported success)** turned
on the *acceptance process itself*: "all green" is a reported success, and we trusted it
without observing the one effect that mattered (the program running). Three generalizable
rules follow, none bound to this feature:

1. **Every integration seam owns a no-mock smoke oracle.** At least one acceptance test
   must drive the *real* entry point (`main()`/console script) with the real internal
   wiring, stubbing only the outermost external boundary (network / live portal / 3rd
   party). If the only test of the entry point mocks the very functions whose
   *interaction* is the risk, the seam is untested by construction — and that is precisely
   where the fatal `Config.load → run` `IndexError` lived.

2. **A safety-critical criterion may not have a waivable-only oracle.** If a behavior is
   the reason the tool is permitted to exist (here: no-submit, no-credentials), its oracle
   must be automatable and non-waivable. Before stamping any criterion `[no-oracle]`, the
   planner must *prove no offline oracle exists* — here one plainly did (real `fill_reply`
   against captured HTML via `file://`; structural assertion for no-submit / no-creds).
   `[no-oracle]` is a justified last resort, never the default for anything live-adjacent.

3. **"Waived" and "deferred" are not "done."** A task state that renders an unrun
   verification as a checked box makes the artifact's "all boxes checked" a lie about its
   riskiest parts. Waived live-verification must render as a distinct, visible, not-done
   state, and a change carrying unrun safety checks cannot present as closed.

**Precedent for future plans:** quarantining a top risk behind a manual checklist
*relocates* the risk, it does not *retire* it — and at the gate, a relocated safety risk
in a waivable step is indistinguishable from no check at all. Decompose so the riskiest
seam and the defining guarantee are the *first* things an automatable oracle pins down,
not the last things a checklist defers.

### Resolution (design triage, 2026-06-02)

Addressing the **Decision Needed**, and reshaped by the operator's two directives — *"the
problem isn't the agentic busy work, it's the HUMAN busy work"* and *"if I'm going to do
any validation, it must be a smooth user experience — this is critical."*

- **(A) No-mock entry-point smoke gate — ADOPTED** as **T024**. Drives the real
  `Config.load → _load_overrides → run` wiring to a *defined* state with only
  `browser_factory` stubbed at the outermost boundary; `cli.py` is non-exempt, so its G2
  fires. This gates the exact seam the `IndexError` hid in. Plan policy for this feature:
  any task touching the entry point / integration seam owns a no-mock smoke oracle.
- **(B) Safety criteria are no longer `[no-oracle]`-waivable — ADOPTED.** Every safety
  criterion gains an automatable offline oracle: no-submit → **T021** (structural,
  source-level absence proof); fill/runtime-type-detect/read-back → **T022** (the *real*
  `fill_reply` against the captured Quill `fixtures/reply_form.html` via `file://`);
  no-credentials → **T023** (structural); login-pause → the captured `login_page.html`
  fixture test + pause-logic test. `spec.md` §4.2 v0.2 now marks **zero** safety criteria
  `[no-oracle]`. The single surviving `[no-oracle]` (T026) is live-drift residue carried as
  a DEFERRED state, not a checkbox.
- **(C) "Waived" ≠ "done" — ADOPTED.** **DEFERRED** is now a first-class state; the four
  waived boxes (T009/T013/T016/T019) are flipped to `[ ] DEFERRED`; SC-007 makes any change
  carrying a DEFERRED safety check **PROVISIONAL**, not done. US1 (no portal) still reaches
  genuine *done* independently.
- **(D) Coverage honesty — ADOPTED in substance.** Rather than litigate coverage
  accounting, (A)+(B) make the real path exercised by *real* wiring and the safety
  guarantees pinned by *real* surfaces; coverage % is explicitly demoted as a completeness
  signal (it never measured the seam). A fake-driven entry-point test does not substitute
  for the T024 smoke gate.
- **Re-open the spec acceptance? — YES, done.** `spec.md` is at **v0.2**: §4.2 acceptance
  criteria (the broken contract) rewritten, FR-017/FR-018 and SC-005/006/007 added. The
  change is re-opened to **PROVISIONAL** and may close only when **either** T026 is run
  green (→ live-verified) **or** the operator explicitly accepts the named live-unverified
  residue in `sign-off.md`. Either way, "done while unrun and unverified" is no longer
  reachable.

**Operator-facing scope:** US1 (reason-and-draft engine) is the genuinely *done*,
fully-verifiable product. The portal pipeline (US2–US4) is now offline-verified (T021–T025,
all agent work) and PROVISIONAL pending the one smooth `discuss validate` run (T026). The
human's entire remaining burden is: log in once, press a key at each checkpoint.

---

## Escalation #2 — 2026-06-02 11:03

**Trigger:** Assumption failure (the plan's live-navigation + auth approach assumed a
server-rendered portal and a persistent session; the live portal is a client-rendered SPA
behind a ForgeRock SSO that redirects on an expired/non-persistent session — and the offline
oracles structurally cannot catch it)
**Blocked at:** Task T026 — Single smooth guided validation run (the first real live
execution of the portal pipeline)

### Completed Successfully
- **All Phase 8 offline correctives (T021–T025, T027) built, G3-certified, committed.** The
  full G3 panel (spec-match / regression / invariants / quality, context-starved) cleared
  "code-verified + human-residue (T026 live)"; 73/73; every non-exempt module 100% line+branch;
  all 22 `[test:]` tags bind to collected tests. The escalation-#1 wound (self-referential /
  waivable oracles) is genuinely closed for everything offline-observable.
- **FR-018 worked exactly as designed:** the live selector miss self-snapshotted the live DOM
  to `fixtures/navigate_live.html` (preserved as `evidence-navigate_live.html`) and named
  `portal_adapter.py` as the one-file home — the operator hand-captured nothing.
- **Root-caused the live failure** across two operator live runs (incl. one after an
  out-of-band re-login into the tool's own persistent profile).

### What Failed
The very first live run of `discuss validate` missed at the `navigate` step:
`go_to_discussions` navigated to the engagement URL, queried `DISCUSSION_ROWS_SEL`, found no
rows, and (correctly, per FR-018) snapshotted the live DOM. But the snapshot is **not** the
discussions list and **not** a drifted selector — it is a **1.6 KB un-rendered Vue SPA login
shell** (`<title>Login</title>`, empty `<div id="appRoot">`, `data-testid="fr-body-image"` →
ForgeRock). Navigating to `/engagement` **redirected to the ForgeRock SSO login** — the
persistent session was not authenticated.

Three structural mismatches, none a one-file selector value, underlie this:

1. **The live portal (Blackboard Ultra) and its IdP (ForgeRock) are client-rendered SPAs;
   the adapter navigates with `wait_until="domcontentloaded"` and queries/snapshots the DOM
   *immediately* (portal_adapter.py:122-123, 142-143).** Every T002 fixture is a *post-render*
   snapshot, but the live adapter operates *pre-render*. The captured `login_page.html` is the
   *same* ForgeRock IdP rendered (it carries the `"University of Phoenix Login"` marker
   `is_login_page` keys on) — the live shell, captured pre-render, has only `<title>Login</title>`
   and no marker. So the same timing flaw breaks **row detection**, **login detection**, *and*
   makes the **FR-018 diagnostic snapshot** capture ~nothing useful.

2. **The auth check is mis-sequenced.** `_run_validate` (and `run`) call
   `browser.ensure_logged_in(page)` on the freshly-opened `about:blank` context page **before**
   `go_to_discussions` ever navigates (cli.py:218), so the FR-003 manual-login pause can never
   see the post-navigation login redirect. The operator is shown an opaque "navigate selector
   miss," not the "please log in" pause the spec promises.

3. **The persistent session did not survive.** After logging into the tool's exact Chromium
   pointed at the tool's exact `--user-data-dir=profile`, then re-running, the **identical**
   login shell came back — suggesting the ForgeRock/UOPX session does not persist across
   separate launches (session-only cookies / device binding?), which challenges FR-002's
   "reuse the operator's existing authenticated session" premise.

Critically, **the offline suite is still 73/73 green** — because it exercises *post-render*
fixtures and the *flow logic*, it structurally cannot reproduce a *pre-render* live timing
failure or a live auth-redirect. This is the live residue the sign-off named ("captured
selectors still match the live portal today … catchable only by the live T026 run"), but the
shape is deeper than selector drift: it is the **whole live-navigation-and-auth strategy**.
And I cannot verify any fix myself — the adapter is coverage-exempt precisely because it is
only honestly exercisable against the live, login-gated portal, so every fix iteration costs
an operator live round-trip with no offline oracle to catch a regression.

### Last Command
```
$ DISCUSS_TARGET_CLASSES=_577963_1 .venv/bin/discuss validate
  # (re-run, AFTER an out-of-band login into the tool's own persistent profile:
  #   /home/qqp/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome \
  #     --user-data-dir=/home/qqp/projects/discuss/profile \
  #     "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"  )
```

### Last Error
```
Selector miss at the 'navigate' step: discussions list did not render for class _577963_1 (no rows matched "div[class*='makeStylescontentListItem']")
Saved the live page markup to fixtures/navigate_live.html for re-capture. Fix the selector in src/discuss/portal_adapter.py — the one-file home for every portal selector.

# fixtures/navigate_live.html (1609 bytes), the actual landing DOM:
<!DOCTYPE html><html lang="en"><head>...<title>Login</title>
<script defer src="js/app.bf2f14ed.js">...</head>
<body class="fr-body-image" data-testid="fr-body-image">
  <noscript>We're sorry but login doesn't work properly without JavaScript enabled...</noscript>
  <div id="appRoot" class="h-100"></div>   <!-- un-rendered ForgeRock SSO login shell -->
</body></html>
```

### Decision Needed
The portal pipeline cannot reach a logged-in page, and the fix is a cross-cutting redesign of
the live-navigation + auth strategy — design's call, not a builder selector swap. Concretely:

- **(A) Condition-based waiting in the adapter.** Replace `wait_until="domcontentloaded"` +
  immediate `query_selector` with waiting for the rendered content — e.g.
  `page.wait_for_selector(rows OR login-marker, timeout=…)`, or `wait_until="networkidle"`,
  across `go_to_discussions` / `open_discussion` / `extract_prompt`. Should FR-018 also
  snapshot *after* render so the diagnostic is useful? What timeout stays "human-paced" (P-I)
  without a tight poll?
- **(B) Re-sequence auth: navigate → wait → detect login-vs-content → pause (FR-003) → retry.**
  Move `ensure_logged_in` to *after* the first portal navigation (so it sees the redirect),
  and have `go_to_discussions` raise `NotAuthenticated` (not `SelectorMiss`) when it lands on
  the login page, so `validate`/`run` can pause for manual login and retry **within the same
  context** (where the just-established session is valid). This modifies the G3-certified
  `validate` flow — re-open it under the plan?
- **(C) Login-page detection for the SPA shell.** The pre-render shell lacks the
  `"University of Phoenix Login"` marker; detect via title `Login` / `fr-body-image` / the URL
  host, or simply wait for render so the existing marker works. Does this need a *new*
  un-rendered-login fixture for an offline timing oracle (`is_login_page` is non-exempt)?
- **(D) Session persistence (FR-002).** If the UOPX/ForgeRock session genuinely does not
  persist across launches, the "reuse the persistent authenticated session" premise needs
  revisiting — accept "log in once per run" (pause-and-retry within the run), or investigate
  the profile/cookie persistence. Which?
- **(E) Verification model.** Every fix here is verifiable *only* live, by the operator. Should
  the plan provision an explicit fix→operator-live-run iteration loop for the adapter, and
  acknowledge the offline oracles cannot gate the pre-render/auth seam (only post-render
  parsing + flow logic)?

Does adopting A–E re-open `spec.md`/`plan.md` (FR-002 session model, FR-003 sequencing,
FR-004 navigation waiting, FR-018 capture timing), and which combination becomes the plan?

### Builder's Perspective
I built and G3-certified every offline corrective and felt genuinely good about it — and then
the very first real `discuss validate` walked straight into a wall I had no way to see coming
from inside the tests, because every fixture I had was a photograph of the portal *after* it
finished painting, while the live tool was reading the DOM the instant it loaded. The "selector
miss at navigate" message was a red herring of my own design: the rows weren't missing because
a class name churned, they were missing because we'd been bounced to a JavaScript login page
that hadn't even rendered yet, and our login detector was looking for a marker that only exists
once the page paints. What unsettles me most is that I asked the operator to log in to the
tool's own profile and re-run, and the *exact same* 1.6 KB shell came back — so either the
session doesn't persist at all or I'm missing something only the live environment can tell me,
and I have no offline oracle to decide which. I kept wanting to "just add a wait and a pause,"
but I'd be writing blind changes to coverage-exempt code, spending the operator's live runs as
my only test harness, and quietly re-opening the `validate` flow I'd just had four independent
reviewers bless — and the load-bearing realization is that the offline green I worked so hard
for is, for this exact seam, structurally incapable of telling me whether the tool actually
works against the real portal.

### Generalizable Lesson

The builder's load-bearing observation — "every fixture I had was a photograph of the
portal *after* it finished painting, while the live tool was reading the DOM the instant it
loaded" — names a failure mode that survives even a *perfect* application of Escalation #1's
corrective. Escalation #1 retired **self-referential** oracles (fakes the author also wrote)
and **waivable** oracles (checklists the operator could skip). This change had *neither*:
every oracle here is non-mock and non-waivable, the suite is honestly 73/73 — and it still
walked straight into a wall. The reason is a third oracle pathology, orthogonal to the first
two:

1. **Rule — a fixture is honest only at the lifecycle state the production code observes.**
   "Use real captured HTML" (Constitution §2) is necessary but not sufficient. A real
   snapshot taken *post-render* is a faithful photograph of a state the live code never reads
   first, because the adapter queries *pre-render* (`wait_until="domcontentloaded"` +
   immediate `query_selector`, portal_adapter.py:122-123/142-143). The HTML was real; it was
   real *at the wrong moment*. Before trusting a captured fixture, name **when in the
   target's state machine it was captured** and confirm the code under test reads it at that
   same point. A timing/lifecycle-state mismatch is invisible to "is this real HTML?" — the
   HTML is real, only the moment is wrong. This is **P-IV (observed effect ≠ reported
   success)** turned on the *observation instrument*: the fixture reported "this is the
   portal," but the effect the live code sees is a different, earlier state.

2. **Pattern — a self-diagnostic inherits the bug it diagnoses if it fires at the same
   broken moment.** FR-018's self-snapshot was a genuinely good mechanism, but because it
   captured at the same pre-render instant the miss was detected, it photographed the 1.6 KB
   un-rendered shell instead of useful markup — the diagnostic was exactly as blind as the
   failure it was meant to explain. When you build a capture-on-failure diagnostic, capture
   at the lifecycle point where the **information is present** (post-render), which is
   deliberately a *different* point than where the failure tripped.

3. **Precedent — when you defer an irreducibly-live residue, name its possible SHAPES, not
   just its cheapest one.** The spec *correctly* named a deferred live residue — but described
   it only as "do today's captured selectors still match the live portal," framing the live
   risk as a one-file selector-*value* swap with a one-file recovery. The actual live risk was
   architectural: a client-rendered SPA + an SSO redirect + a possibly non-persistent
   session, whose recovery is a cross-cutting redesign of navigation, auth-sequencing, and
   capture timing. Under-specifying the *shape* of a deferred risk makes the plan
   under-provision for it (a "one-file fix" recovery budget against a cross-cutting-redesign
   reality). A deferred-live item must enumerate the *kinds* of failure it stands in for —
   value drift? rendering-lifecycle? auth-flow? session-lifetime? — so the recovery budget
   matches the actual blast radius, not the cheapest imagined one. Grounding: this is the
   environment/OS-primitive-lifetime + operation-success≠observed-effect cluster — two
   load-bearing *environment* assumptions ("the portal renders server-side enough to read
   immediately" and "the authenticated session survives a fresh launch") baked in silently
   rather than surfaced as assumptions and routed to a validation item.

**Corollary for this method, carrying Escalation #1 forward:** the builder concluded "every
fix here is verifiable *only* live." That is itself an instance of pathology (2) — reasoning
from the broken moment. FR-018's self-snapshot already produced `evidence-navigate_live.html`,
a *real* pre-render ForgeRock shell; that artifact converts the login-detection fix into an
**offline, non-exempt oracle** (`is_login_page` / a `classify_landing` predicate in
`portal_parse`). The same corrective Escalation #1 demanded — *prove no offline oracle exists
before stamping `[no-oracle]`* — applies recursively: a captured-on-failure artifact is not
just a re-capture target, it is a new offline oracle. Only the *render-timing* and
*session-persistence* behaviours are irreducibly live after that.

### Resolution (design triage, 2026-06-02)

Addressing the **Decision Needed (A–E)**, and reshaped by the operator's load-bearing
constraint surfaced in triage — *"if the session doesn't persist the operator might need to
perform a two-step verification too; that would not be acceptable to do every single time."*
That single fact flips persistence from a deferrable convenience into a **blocking
precondition**, and is why my first recommendation ("defer persistence, accept once-per-run
login") was wrong and was overridden.

- **(A) Condition-based waiting — ADOPTED** as **T030**. `wait_for_selector(rows OR
  login-marker, bounded human-paced timeout)` replaces `domcontentloaded` + immediate query
  across the three nav/extract methods; FR-018 snapshots *after* the wait. `wait_for_selector`
  is mutation-observer-based, not a tight poll → P-I-clean. spec FR-004/FR-018 updated.
- **(B) Re-sequence auth — ADOPTED** as **T029**. `ensure_logged_in` moves *after* the first
  navigation, in the same context, with one bounded retry; the pre-nav `about:blank` check is
  removed. This **re-opens the G3-certified `run`/`validate` flow** — which is exactly what an
  escalation does (Escalation #1 did the same); the no-mock smoke (T024) is *extended*, not
  bypassed, to gate the new seam. spec FR-003 updated.
- **(C) Login detection for the SPA shell — ADOPTED, and OFFLINE** as **T028**. The builder's
  framing "every fix here is verifiable only live" was itself the escalation's pathology #2
  (reasoning from the broken moment): FR-018 already produced `evidence-navigate_live.html`, a
  *real* pre-render ForgeRock shell. That artifact becomes `fixtures/login_shell_prerender.html`
  and makes `classify_landing` / `is_login_page` a **real, non-exempt, falsifiable** oracle —
  not a live residue. Login-classification and auth-sequencing both leave the `[no-oracle]`
  column. spec adds the `test_classify_prerender_login_shell` and
  `test_auth_pause_is_post_navigation_with_retry` criteria.
- **(D) Session persistence — RESOLVED to BLOCKING (operator fork)** as **T031** + **SC-008**.
  The persistence premise is *not* softened (my proposed softening was wrong against the 2FA
  fact); it is *strengthened* into a measurable, blocking live check: a second run must reach
  content **without re-login or re-2FA**. Mitigation in the design: the operator selects "keep
  me signed in / trust this device" at first login so ForgeRock issues persistent SSO cookies.
  Contingency if persistence is genuinely impossible: attach to the operator's already
  authenticated running browser (CDP) — a **new spec-level fork**, re-escalated, not assumed.
  FR-002/§5 updated; the change stays PROVISIONAL until T031 PASSes.
- **(E) Verification model — RESOLVED.** The seam is *not* "verifiable only live." Split:
  **offline-pinned** = login-classification (T028, real fixture) + auth re-sequencing (T029,
  no-mock smoke); **irreducibly live** = SPA render-timing (T026) + session persistence (T031).
  Two named DEFERRED items, both distinct from "done", neither hidden behind `[no-oracle]`
  green. No standing fix→live-run loop is provisioned beyond these — the offline oracles now
  catch regressions in everything except timing and persistence, which the one operator sitting
  (T026 then T031) confirms.

**Re-open the spec? — YES, done.** `spec.md` → **v0.3** (FR-002/003/004/018, SC-008, 4 new
EARS criteria, §3.3 three-axis residue shape, §5 assumptions). `plan.md` → **v2** (the four
redesign architecture decisions, the grown offline oracle layer, risks 6–7). `tasks.md` adds
**Phase 9 (T028–T031)**. The handoff signature is reset to UNSIGNED — the artifacts changed,
so the operator re-signs the corrected, G1-recleared plan (the floor is signature-independent;
panel-before-sign-off).

**Operator-facing scope:** US1 (reason-and-draft engine) remains genuinely *done*. The portal
pipeline gains an offline-pinned redesign (T028/T029, agent work) plus a coverage-exempt
adapter change (T030, agent work). The human's remaining burden is **one sitting**: run
`discuss validate`, log in by hand once (choose "trust this device"), confirm the checkpoints,
then run it a second time to confirm no re-2FA. If that second run still demands 2FA, the tool
isn't acceptable as designed and the auth model re-escalates.

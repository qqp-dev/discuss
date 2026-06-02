# Selector capture & live-verification checklist (T002)

This is the **operator checklist** for the one manual step the build cannot do for you:
capturing the real UOPX portal markup. The UOPX portal is a proprietary, login-gated DOM
we do not control and cannot guess (spec §3.3), so the real selectors, the due-date
format, and four saved HTML fixtures must be captured against the **live, logged-in**
portal during build. This file is also the **re-verification checklist** — re-run the
"Verify" section after any portal change; a markup change is a one-file fix in
`src/discuss/portal_adapter.py`.

> **Status:** the checklist and the `SELECTORS` scaffold were prepared by the build. The
> capture itself (steps below) is pending — do it once, fill the values, commit the
> fixtures, then check T002 off in `tasks.md`. Nothing in the live pipeline (T006,
> T010–T013, T015–T017, T019) can be completed until this is done.

## 0. Prerequisites

```bash
# from the project root, with the project venv active (or use its bin on PATH)
pip install -e '.[dev]'
python -m playwright install chromium      # one-time: download the browser binary
```

Decide a persistent profile dir (default `profile/`, gitignored). The browser reuses your
own human-authenticated session — **no credentials are ever stored** (FR-002, P-I).

## 1. Capture the four fixtures

Run this capture helper (paste into a scratch file, e.g. `scratch_capture.py`, and run it
with the venv python). It opens a **persistent** browser you log into by hand, then saves
each page's HTML on an Enter prompt. Save four pages:

```python
# scratch_capture.py — throwaway capture helper (do not commit)
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path("fixtures"); OUT.mkdir(exist_ok=True)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context("profile", headless=False)
    page = ctx.pages[0] if ctx.pages else ctx.new_page()

    page.goto("https://www.phoenix.edu/")          # adjust to the real portal entry URL
    input("LOGGED-OUT login page is showing? Enter to save login_page.html… ")
    (OUT / "login_page.html").write_text(page.content(), encoding="utf-8")

    input("Now LOG IN by hand and navigate to the discussions list. Enter to save… ")
    (OUT / "discussions_list.html").write_text(page.content(), encoding="utf-8")

    input("Open ONE discussion (the prompt is visible). Enter to save… ")
    (OUT / "discussion_page.html").write_text(page.content(), encoding="utf-8")

    input("Open/scroll to the REPLY form on that discussion. Enter to save… ")
    (OUT / "reply_form.html").write_text(page.content(), encoding="utf-8")

    ctx.close()
```

You should now have, committed under `fixtures/`:
- [ ] `login_page.html` (logged-out)
- [ ] `discussions_list.html`
- [ ] `discussion_page.html`
- [ ] `reply_form.html`

> Scrub anything personal/identifying from the saved HTML before committing if needed; the
> fixtures only need the structural markup the parsers target.

## 2. Record the selectors

Inspect the saved HTML (browser devtools on the live page, or the saved files) and record a
stable selector for each. Fill them into `src/discuss/portal_adapter.py` `SELECTORS = {…}`:

| Key | What it selects | Notes |
|-----|-----------------|-------|
| `class_link` | the control opening a class's discussions area | the click-path step |
| `discussion_rows` | each discussion row/card on the list | iterated for selection |
| `due_date_cell` | the due-date text within a row | basis for soonest-due |
| `discussion_link` | the link/title that opens a discussion | per row |
| `prompt_container` | the prompt's plaintext container on a discussion page | extracted text source |
| `reply_field` | the reply textarea / rich-text editor | type detected at runtime, FR-011 |

Also record the **due-date string format** (a `strptime` pattern, e.g. `%b %d, %Y`) seen in
`due_date_cell`, into `portal_adapter.py` `DUE_DATE_FORMAT` — `portal_parse.parse_discussions`
uses it.

Note a **login-page marker** too (a URL fragment and/or an element present only on the
logged-out login screen). `portal_parse.is_login_page(url, html)` (T006) keys off it to
decide when to pause for manual login (FR-003).

- [ ] all six `SELECTORS` filled (no empty strings remain)
- [ ] `DUE_DATE_FORMAT` filled
- [ ] login-page marker decided (for T006's `is_login_page`)

## 3. Verify (the re-runnable live checklist)

Run these against the live portal after capture, and again after any portal change. A
markup change should only ever require editing `portal_adapter.py`.

- [ ] **Navigated correctly** — the click-path lands on the discussions list for the
      configured class.
- [ ] **Selected the soonest-due** — the discussion the tool picks is the one with the
      nearest *upcoming* due date (not a past one).
- [ ] **Extracted the right prompt** — the extracted plaintext matches the prompt shown on
      the page.
- [ ] **Filled field shows the text** — after fill, the reply field's rendered content
      equals the response (read-back verified).
- [ ] **Did NOT submit** — the reply is left unsubmitted; nothing was posted.
- [ ] **No credentials stored** — `profile/` holds a session, never a written credential.

---

## Live verification sections (appended by later tasks)

The story-level live tasks append their own checklist sections below as they are run:
- **T009 — US1 session:** input solicited before draft? editor blocked until close?
  `response.md` = the edited text?
- **T013 — US2 discover/extract:** lands on soonest-due; confirmation gate names the right
  discussion + due date; extracted text matches the page.
- **T016 — US3 fill:** rendered field equals the response; nothing submitted; an
  artificially-undetectable field aborts write-back and preserves `response.md`.
- **T019 — US4 end-to-end + login-pause:** launcher → full pipeline to a filled,
  unsubmitted reply on the soonest-due discussion; a logged-out start pauses for manual
  login then continues; no credential written; no submit.

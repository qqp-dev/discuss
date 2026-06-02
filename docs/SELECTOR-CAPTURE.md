# Selector capture & live-verification checklist (T002)

This is the **operator checklist** for the one manual step the build cannot do for you:
capturing the real UOPX portal markup. The UOPX portal is a proprietary, login-gated DOM
we do not control and cannot guess (spec §3.3), so the real selectors, the due-date
format, and four saved HTML fixtures must be captured against the **live, logged-in**
portal during build. This file is also the **re-verification checklist** — re-run the
"Verify" section after any portal change; a markup change is a one-file fix in
`src/discuss/portal_adapter.py`.

> **Status:** capture **done** (T002). The four fixtures are committed under `fixtures/`,
> `SELECTORS` + `DUE_DATE_FORMAT` + `LOGIN_PAGE_MARKER` are filled in
> `src/discuss/portal_adapter.py`, and the selectors were validated against the saved
> fixtures via the real selector engine (7 discussion rows, 5 dated; prompt = first
> `#bb-editor-textbox`; login marker confirmed). This file is now the **re-verification
> checklist**: re-run the "Verify" section (§3) against the live portal after any portal
> change — a markup change is a one-file fix in `portal_adapter.py`. The live story-level
> checks (T009 session, T013 discover/extract, T016 fill, T019 end-to-end + login-pause)
> are the remaining operator runs against the real portal.

## 0. Prerequisites

```bash
# from the project root — create and activate a virtualenv first. (A bare `pip install`
# hits PEP-668 "externally-managed-environment" on Debian's system Python; a venv avoids
# that and pins one interpreter, since this box has both Debian 3.12 and linuxbrew 3.14.)
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m playwright install chromium      # one-time: download the browser binary
```

> All later commands in this file assume that venv is active (or use `.venv/bin/python`,
> `.venv/bin/pytest`, `.venv/bin/discuss` explicitly).

Decide a persistent profile dir (default `profile/`, gitignored). The browser reuses your
own human-authenticated session — **no credentials are ever stored** (FR-002, P-I).

## 1. Capture the four fixtures

Run this capture helper (paste into a scratch file, e.g. `scratch_capture.py`, in the
**project root**, and run it with the venv python: `.venv/bin/python scratch_capture.py`).
It opens a **persistent** browser you log into by hand, then saves each page's HTML on an
Enter prompt. The helper is deliberately defensive about the one failure mode that bites
here — login bounces `www.phoenix.edu` → `my.phoenix.edu` and opens views in new tabs, so
a single fixed `ctx.pages[0]` handle goes stale and silently re-saves the same Home page.
So it **re-resolves the tab you're actually looking at on every save**, **prints the URL +
title** it captured, and **refuses to save a page byte-identical to one already saved**.
Save four pages:

```python
# scratch_capture.py — throwaway capture helper (do not commit).
# Run from the project root with the venv python: .venv/bin/python scratch_capture.py
import hashlib
import sys
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ModuleNotFoundError:  # wrong interpreter — usually a stale activated venv shadows it
    _venv = Path(__file__).resolve().parent / ".venv" / "bin" / "python"
    sys.exit(
        f"playwright is not installed in this interpreter ({sys.executable}).\n"
        "You're probably running a different python than the project venv (an activated\n"
        "venv from elsewhere shadows a bare `python`). Re-run naming the venv explicitly:\n"
        f"    {_venv} {Path(__file__).name}"
    )

# Refuse to run anywhere but the project root, so fixtures never again land somewhere
# stray (a CWD-relative OUT is how an earlier run wrote four files onto the Desktop).
if not (Path("pyproject.toml").exists() and Path("src/discuss").is_dir()):
    sys.exit("Run this from the discuss project root (where pyproject.toml lives).")

OUT = Path("fixtures").resolve()
OUT.mkdir(exist_ok=True)
print(f"Saving fixtures to {OUT}")

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context("profile", headless=False)
    saved: dict[str, str] = {}  # content-hash -> filename already written

    def active_page():
        """The tab the operator is actually viewing — re-resolved on every save.

        Prefer a non-hidden tab (a background tab reports visibilityState 'hidden' even
        while the terminal holds OS focus), newest first. This is what stops the stale
        `ctx.pages[0]` from silently capturing Home three times.
        """
        pages = [pg for pg in ctx.pages if not pg.is_closed()]
        visible = []
        for pg in pages:
            try:
                if pg.evaluate("document.visibilityState") == "visible":
                    visible.append(pg)
            except Exception:
                pass  # a navigating/closing tab can't be evaluated; skip it
        candidates = visible or pages
        return candidates[-1] if candidates else ctx.new_page()

    def save(name, prompt):
        """Prompt, capture the active tab — but refuse a byte-identical repeat."""
        while True:
            input(prompt)
            page = active_page()
            html = page.content()
            print(f"  -> {page.title()!r}  {page.url}")
            digest = hashlib.sha256(html.encode("utf-8")).hexdigest()
            if digest in saved:
                print(f"  !! byte-identical to {saved[digest]} — you're still on the same "
                      "page (navigate to the right view, or the helper read the wrong "
                      "tab). Enter to retry, or type 'force' to save anyway.")
                if input("  retry/force> ").strip().lower() != "force":
                    continue
            (OUT / name).write_text(html, encoding="utf-8")
            saved[digest] = name
            print(f"  saved {name} ({len(html):,} bytes)")
            return

    start = ctx.pages[0] if ctx.pages else ctx.new_page()
    start.goto("https://www.phoenix.edu/")  # adjust to the real portal entry URL if needed

    save("login_page.html",
         "LOGGED-OUT login page is showing? Enter to save login_page.html… ")
    save("discussions_list.html",
         "LOG IN by hand and navigate to the discussions list. Enter to save… ")
    save("discussion_page.html",
         "Open ONE discussion (the prompt is visible). Enter to save… ")
    save("reply_form.html",
         "Open/scroll to the REPLY form on that discussion. Enter to save… ")

    ctx.close()
```

Watch the `-> '<title>'  <url>` line each save prints: if it says `'Home'` (the
`my.phoenix.edu` dashboard) when you meant the discussions list, you're on the wrong tab —
navigate to the right view and let the identical-page guard re-prompt you.

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

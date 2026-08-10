# discuss

Single-trigger, **assisted** discussion-post draft pipeline for the University of Phoenix
(UOPX / Blackboard Ultra) student portal.

One trigger opens your already-logged-in browser, finds this week's soonest-due
discussion, then shows a small menu: draft/fill the **main post**, or draft the **two
required classmate replies**. Main-post mode drops the edited response into the portal's
reply field - and **stops there**. Peer-reply mode saves two edited drafts for you to paste
manually under classmates' posts.

> **What this tool will never do** (these are ratified statements in `intent.md`,
> the project's single source of truth):
> - **Never submits** a post. Main-post mode fills the reply field and leaves it for you.
> - **Never stores or types your credentials.** You log in by hand; it reuses your session.
> - **Never auto-generates** a reply without your input. The drafting session asks for your
>   stance and evidence first.
> - **Acts at human pace** — no automated hammering of the portal.

It assists *your* post; it does not write posts for you to submit unread.

---

## Requirements

- Linux desktop (the launcher targets freedesktop `.desktop` / common terminal emulators).
- Python **3.11+**.
- A UOPX portal account you log into yourself.

## Install

Run the setup script once — it handles everything (Python environment, browser download,
course ID, and desktop launcher):

```bash
bash setup.sh
```

When it finishes, a **Discuss** icon appears in your applications menu (and Desktop if one
exists). From then on, just click that icon to start a run.

## First-time login (one-time per machine)

The tool drives a **persistent** browser profile (default `<project>/profile/`,
gitignored) that holds *your* session — it never sees a password. Establish that session
once:

1. Run `discuss` (or click the launcher). A real Chromium window opens and the tool
   navigates to your portal.
2. If that navigation redirects to the UOPX login (the SSO login screen), the tool
   **pauses** and prompts you in the terminal. Log in by hand in the browser window — and
   choose **"keep me signed in" / "trust this device"** when offered, so the portal issues a
   *persistent* session and you are **not** asked to repeat two-step verification on every
   run. Then press **Enter** in the terminal; the tool retries the navigation and continues.
3. The session is now saved in the project-root `profile/`; future runs reuse it directly —
   they go straight to your discussions with no fresh login or repeat 2FA, until the session
   genuinely expires (then you just log in by hand once more on the next run).

No credential is ever read from or written to disk by the tool.

## Configure (`.env` and environment variables)

Setup saves plain `KEY=value` configuration in the project-root `.env`. The `discuss` CLI
reads that same file itself on every launch, whether started from a desktop shortcut or by
calling `.venv/bin/discuss` directly from any working directory. Process-environment values
win over values in `.env`, so an inline override remains available. Each setting is optional
except the target class:

| Variable | Meaning | Default |
|---|---|---|
| `DISCUSS_TARGET_CLASSES` | **required** — comma-separated class id(s) to search. Find the id in the course URL: `.../ultra/courses/<class_id>/...` | (none — run aborts with guidance if unset) |
| `DISCUSS_EDITOR` | the `--wait`-style GUI editor command for editing the draft (must block until you close it) | `xed --wait` |
| `DISCUSS_PROFILE_DIR` | persistent browser profile dir (holds your session; no credentials) | project-root `profile/` |
| `DISCUSS_RUN_ROOT` | parent dir for per-run working dirs | project-root `runs/` |
| `DISCUSS_CONFIRM` | set to `0`/`false`/`no`/`off` to disable the pre-extraction confirmation gate | gate **on** |
| `DISCUSS_MODE` | optional shortcut that skips the menu; use `main` or `peer` | (menu shown) |

The editor must **block** until you save and close. The default `xed --wait` is the stock
Linux Mint Cinnamon text editor. Unless explicitly overridden, both desktop and terminal
launches use the same project-root browser profile and run archive regardless of launch CWD.

## Run it

**Double-click the Discuss icon** in your applications menu or Desktop shortcut.

To update the saved course ID or run from a terminal:

```bash
bash update-course.sh
# run directly after setup (works from any CWD when invoked by its path):
/path/to/discuss/.venv/bin/discuss
```

The updater changes only `DISCUSS_TARGET_CLASSES` in the project-root `.env`; it preserves
all other settings and reports the exact value and file it saved.

### What a run looks like

1. Opens your persistent browser; pauses for manual login if needed.
2. Navigates to your class's discussions and selects the **soonest upcoming due** one
   (past-due and undated discussions are skipped). If nothing is upcoming, it stops and
   reports the searched class ID, discussions found, count with parseable due dates, the
   parseable date range (or that there were no parseable dates), and today's date. Guided
   `discuss validate` reports the same evidence instead of treating an empty week as an
   unexplained result.
3. Shows a menu:
   - `1) Main post`
   - `2) Two classmate replies`
4. Shows a **confirmation** naming the discussion, due date, and selected work mode.
   Decline and nothing is extracted. (You can disable this gate in config; it defaults
   **on**.)
5. In **main post** mode, the tool extracts the prompt to the project-root
   `runs/<run>/prompt.md`, starts a
   primed drafting session that **asks you** for your stance / main points / evidence,
   opens `response.md` in `xed`, then injects the edited text into the reply field,
   **verifies the read-back**, and leaves the browser open with the unsubmitted draft.
   **You review and submit.**
6. In **classmate replies** mode, the tool extracts the prompt plus visible classmate posts
   to `prompt.md` and `peer-posts.md`, asks for the through-line from your main post,
   chooses two usable classmates, opens `peer-reply-1.md` and `peer-reply-2.md` in `xed`,
   then stops. You paste those replies manually into the selected classmate reply forms.

If the main-post field can't be found or the read-back doesn't match, it does **not** write
to the portal - your `response.md` is preserved and you're told to paste it manually.

---

## After a portal change (re-verification)

The UOPX portal is a proprietary DOM we don't control. **Every portal-specific selector
lives in exactly one file — `src/discuss/portal_adapter.py`** — so a markup change is a
one-file fix. If a run fails with a `SelectorMiss` (it names the step), re-capture and
re-verify using the operator checklist:

→ **`docs/SELECTOR-CAPTURE.md`** — how to capture the four reference fixtures, record the
selectors + due-date format, and run the live "Verify" checklist (navigated correctly?
selected the soonest-due? extracted the right prompt? field shows the text? **did NOT
submit?** no credentials stored?).

## Development

```bash
.venv/bin/pytest                 # run the test suite
.venv/bin/pytest --cov=discuss --cov-branch   # with coverage
```

Pure logic (parsing, selection, read-back verification, config, file handoff) is unit-tested
against saved-HTML fixtures and carries line/branch coverage. The live portal adapter and
the interactive session are coverage-exempt and verified by the `docs/SELECTOR-CAPTURE.md`
checklist against the real portal — by design, CI never touches the login-gated portal.

## Principles

The project's governing statements live in **`intent.md`** — the single source of truth,
every line ratified by the operator. The guarantees above (never submits, never touches
credentials, never auto-generates, human pace, fail-loud with your drafts preserved, one
adapter file for the portal) are stated there in full; where this README and `intent.md`
disagree, `intent.md` wins.

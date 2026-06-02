# discuss

Single-trigger, **assisted** discussion-post draft pipeline for the University of Phoenix
(UOPX / Blackboard Ultra) student portal.

One trigger does the whole loop: open your already-logged-in browser, find this week's
soonest-due discussion, pull out the prompt, help you think through and draft a reply in a
GUI editor, then drop that reply into the portal's reply field — and **stop there**. You
review and submit the post yourself.

> **What this tool will never do** (these are guarantees, see *Principles* below):
> - **Never submits** a post. It fills the reply field and leaves it for you.
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

From the project root, create a virtualenv and install (a bare `pip install` hits
PEP-668 "externally-managed-environment" on Debian's system Python; a venv avoids that):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python -m playwright install chromium    # one-time: download the browser binary
```

This puts a `discuss` console-script on your PATH (inside the venv).

## First-time login (one-time per machine)

The tool drives a **persistent** browser profile (default `./profile/`, gitignored) that
holds *your* session — it never sees a password. Establish that session once:

1. Run `discuss` (or click the launcher). A real Chromium window opens.
2. If you land on the UOPX login page, the tool **pauses** and prompts you in the terminal.
   Log in by hand in the browser window, then press **Enter** in the terminal to continue.
3. The session is now saved in `profile/`; future runs reuse it until it expires (then you
   just log in by hand again on the next run).

No credential is ever read from or written to disk by the tool (FR-002).

## Configure (environment variables)

`discuss` reads its configuration from the environment (each var is optional except the
target class):

| Variable | Meaning | Default |
|---|---|---|
| `DISCUSS_TARGET_CLASSES` | **required** — comma-separated class id(s) to search. Find the id in the course URL: `.../ultra/courses/<class_id>/...` | (none — run aborts with guidance if unset) |
| `DISCUSS_EDITOR` | the `--wait`-style GUI editor command for editing the draft (must block until you close it) | `code --wait` |
| `DISCUSS_PROFILE_DIR` | persistent browser profile dir (holds your session; no credentials) | `profile/` |
| `DISCUSS_RUN_ROOT` | parent dir for per-run working dirs | `runs/` |
| `DISCUSS_CONFIRM` | set to `0`/`false`/`no`/`off` to disable the pre-extraction confirmation gate | gate **on** |

The editor must **block** until you save and close (the default `code --wait` is VS Code).
If VS Code isn't installed, use a terminal editor that blocks (`DISCUSS_EDITOR=nano`) or a
GUI one (`DISCUSS_EDITOR='gnome-text-editor --standalone'`).

## Run it

Either:

- **Launcher (double-click):** install the desktop entry so a double-click starts a run.
  ```bash
  # Edit launcher/discuss.desktop's Exec= path if you moved the project, then:
  cp launcher/discuss.desktop ~/.local/share/applications/
  update-desktop-database ~/.local/share/applications 2>/dev/null || true
  ```
  `launch.sh` opens a terminal emulator running `discuss`; the interactive session happens
  inside it. The `discuss` script must be on the PATH of your desktop session (point the
  launcher at the venv, or add the venv `bin` to your session PATH).

- **Terminal:** with the venv active, run with at least the target class set:
  ```bash
  DISCUSS_TARGET_CLASSES=_577963_1 DISCUSS_EDITOR=nano discuss
  ```

### What a run looks like

1. Opens your persistent browser; pauses for manual login if needed.
2. Navigates to your class's discussions and selects the **soonest upcoming due** one
   (past-due and undated discussions are skipped). If nothing is upcoming, it stops and
   says so.
3. Shows a **confirmation** naming the discussion and its due date. Decline and nothing is
   extracted. (You can disable this gate in config; it defaults **on**.)
4. Extracts the prompt to `runs/<run>/prompt.md` and starts a primed drafting session that
   surfaces the prompt's angles, **asks you** for your stance / main points / evidence,
   then drafts `response.md` grounded in your answers.
5. Opens `response.md` in your editor and waits for you to save and close.
6. Injects your final text into the reply field, **verifies the read-back**, and leaves the
   browser open with the unsubmitted draft. **You review and submit.**
   - If the field can't be found or the read-back doesn't match, it does **not** write to
     the portal — your `response.md` is preserved and you're told to paste it manually.

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

- **Respectful guest (P-I).** Human pace, minimum page loads, no automated retry loops, no
  credential automation. We are a guest in someone else's system.
- **Assists, never impersonates (P-II).** The tool helps *you* write *your* post and draws
  out your own stance and evidence; it never fabricates a submission. It fills the reply but
  the submit is always yours.
- **One adapter for the portal (P-III / FR-013).** All portal selectors and live I/O are
  confined to `portal_adapter.py`; everything else is pure and testable.
- **Fail loud (P-IV / FR-014).** Each failure condition raises a specific, named error and
  preserves your work rather than guessing or silently proceeding.

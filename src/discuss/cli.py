"""`discuss` console-script entry point + the orchestrator pipeline (T017).

``run()`` wires the pieces into the one-click flow (FR-001): open the persistent context →
pause for manual login if needed → navigate to the soonest-due discussion → let the
operator choose the work mode → confirm → run the mode-specific drafting handoff. Main-post
mode fills the top-level reply field WITHOUT submitting; peer-reply mode only saves the two
classmate replies for manual paste. The adapter, session, menu, and login/confirm/announce
seams are all injected so the whole pipeline is testable with fakes
(tests/test_cli_pipeline.py); ``main()`` supplies the real implementations and is verified
end-to-end live in T019.
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

from discuss import browser, handoff, portal_adapter
from discuss.config import Config, PROJECT_ROOT
from discuss.errors import (
    DiscussError,
    FillVerifyFailed,
    NoUpcomingDiscussion,
    NotAuthenticated,
    SelectorMiss,
)
from discuss.portal_parse import select_soonest_due

_FALSEY = {"0", "false", "no", "off"}
_DOTENV_FILE = PROJECT_ROOT / ".env"
MODE_MAIN = "main"
MODE_PEER = "peer"
_MODE_LABELS = {
    MODE_MAIN: "main post",
    MODE_PEER: "two classmate replies",
}
_MODE_ALIASES = {
    "1": MODE_MAIN,
    "m": MODE_MAIN,
    "main": MODE_MAIN,
    "post": MODE_MAIN,
    "main-post": MODE_MAIN,
    "main_post": MODE_MAIN,
    "2": MODE_PEER,
    "p": MODE_PEER,
    "peer": MODE_PEER,
    "peers": MODE_PEER,
    "reply": MODE_PEER,
    "replies": MODE_PEER,
    "peer-replies": MODE_PEER,
    "peer_replies": MODE_PEER,
    "classmate": MODE_PEER,
    "classmates": MODE_PEER,
}

# Operator guidance when no target class is configured — shared by the pipeline and the
# `validate` subcommand so the one fail-loud message lives in a single place.
_NO_CLASS_MESSAGE = (
    "discuss: no target class configured. Set DISCUSS_TARGET_CLASSES to one or more "
    "class ids,\n  e.g.  DISCUSS_TARGET_CLASSES=_577963_1 discuss\n"
    "  (find the id in the course URL: .../ultra/courses/<class_id>/...)."
)

# The placeholder reply `discuss validate` injects so the operator can eyeball that the
# fill lands in the right field and renders — it is never submitted (FR-010).
_VALIDATE_SAMPLE = "discuss validate — sample reply (this is NOT submitted)."


def _confirm_via_input(prompt: str) -> bool:
    """Default confirmation gate: ask the operator and accept only an explicit yes."""
    return input(prompt).strip().lower() in ("y", "yes")


def _normalize_mode(value: str) -> str | None:
    """Return the canonical work mode for a menu/env value, or ``None`` if unknown."""
    return _MODE_ALIASES.get(value.strip().lower())


def _choose_mode_via_input() -> str:
    """Default operator menu for picking the kind of discussion work to do."""
    print("What do you want to work on?")
    print("  1) Main post")
    print("  2) Two classmate replies")
    while True:
        choice = input("Select 1 or 2 [1]: ").strip() or "1"
        mode = _normalize_mode(choice)
        if mode is not None:
            return mode
        print("Please choose 1 for the main post or 2 for the classmate replies.")


def _read_dotenv(path: Path) -> dict[str, str]:
    """Read the launcher's deliberately small project config format.

    The setup scripts save plain ``KEY=value`` lines. Blank lines, comments, and malformed
    lines are ignored; no shell expansion or third-party dotenv syntax is attempted.
    """
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key:
            values[key] = value
    return values


def _load_overrides(env=None, *, dotenv_path: Path | None = None) -> dict:
    """Gather config overrides from project ``.env``, then the process environment.

    Process values take precedence over file values. Recognised vars (each absent → no key,
    so the documented default wins):
      DISCUSS_TARGET_CLASSES  comma-separated class ids (e.g. ``_577963_1,_x_2``)
      DISCUSS_EDITOR          a ``--wait``-style editor command (space-separated)
      DISCUSS_PROFILE_DIR     persistent browser profile dir
      DISCUSS_RUN_ROOT        parent dir for per-run working dirs
      DISCUSS_CONFIRM         set to a falsey value (0/false/no/off) to disable the gate
      DISCUSS_MODE            optional shortcut: main or peer (skips the menu)
    """
    if env is None:
        env = os.environ
    merged = _read_dotenv(_DOTENV_FILE if dotenv_path is None else dotenv_path)
    merged.update(env)

    overrides: dict = {}
    classes = merged.get("DISCUSS_TARGET_CLASSES", "").strip()
    if classes:
        overrides["target_classes"] = [c.strip() for c in classes.split(",") if c.strip()]
    editor = merged.get("DISCUSS_EDITOR", "").strip()
    if editor:
        overrides["editor_cmd"] = editor.split()
    profile = merged.get("DISCUSS_PROFILE_DIR", "").strip()
    if profile:
        overrides["profile_dir"] = Path(profile)
    run_root = merged.get("DISCUSS_RUN_ROOT", "").strip()
    if run_root:
        overrides["run_root"] = Path(run_root)
    confirm = merged.get("DISCUSS_CONFIRM", "").strip()
    if confirm:
        overrides["confirm"] = confirm.lower() not in _FALSEY
    mode = merged.get("DISCUSS_MODE", "").strip()
    if mode:
        overrides["mode"] = mode
    return overrides


def _resolve_mode(config: Config, choose_mode) -> str:
    """Resolve the requested work mode from config or the interactive menu."""
    if config.mode:
        mode = _normalize_mode(config.mode)
        if mode is None:
            raise DiscussError(
                f"invalid DISCUSS_MODE {config.mode!r}; use 'main' or 'peer'"
            )
        return mode
    mode = choose_mode()
    if mode not in _MODE_LABELS:
        raise DiscussError(f"invalid work mode {mode!r}; use 'main' or 'peer'")
    return mode


def _no_upcoming_message(class_id: str, discussions, today: dt.date) -> str:
    """Describe the exact class and list evidence behind a no-upcoming result."""
    parseable_dates = [item.due_date for item in discussions if item.due_date is not None]
    if parseable_dates:
        date_range = f"{min(parseable_dates)} to {max(parseable_dates)}"
    else:
        date_range = "none (no parseable due dates)"
    return (
        f"No upcoming discussion for class {class_id}. "
        f"Discussions found: {len(discussions)}. "
        f"Discussions with parseable due dates: {len(parseable_dates)}. "
        f"Parseable due-date range: {date_range}. Today: {today}."
    )


def _navigate_to_discussions(adapter, page, class_id, *, ensure_logged_in, announce) -> None:
    """Navigate to the discussions list, pausing for MANUAL login post-navigation if the
    portal redirects to the SSO login (FR-003, Esc#2).

    The auth check is intentionally AFTER the first navigation: the page opened for a fresh run
    is ``about:blank``, so a login redirect only becomes visible once we navigate to the portal
    (the pre-navigation check the first live run shipped could never see it). ``go_to_discussions``
    raises ``NotAuthenticated`` when it lands on the login page; we then pause for manual login in
    the SAME context (never automating credentials) and retry the navigation EXACTLY once. A
    second ``NotAuthenticated`` propagates — one bounded, human-paced retry, no storm
    (FR-014/FR-016).
    """
    try:
        adapter.go_to_discussions(page, class_id)
        return
    except NotAuthenticated:
        announce(
            "The portal redirected to the login page. Please log in in the open browser "
            "window; the run continues automatically once you are signed in."
        )
    ensure_logged_in(page)  # pause for manual login in the same context (FR-003)
    adapter.go_to_discussions(page, class_id)  # retry ONCE; a second NotAuthenticated propagates


def run(
    *,
    config: Config,
    browser_factory,
    adapter,
    today: dt.date,
    session=handoff.run_session,
    ensure_logged_in=browser.ensure_logged_in,
    make_run_dir=handoff.make_run_dir,
    confirm=_confirm_via_input,
    choose_mode=_choose_mode_via_input,
    announce=print,
) -> None:
    """Run the selected drafting pipeline once. Ordering and safety guarantees:

    1. open the context and navigate — auth is checked AFTER navigation (Esc#2): a login
       redirect pauses for manual login and retries once; a persistent ``NotAuthenticated``
       surfaces and the run cannot proceed;
    2. list + ``select_soonest_due`` — ``None`` → ``NoUpcomingDiscussion`` (stop, extract
       nothing) (FR-014);
    3. show/resolve the work-mode menu (main post vs two classmate replies);
    4. **confirmation gate** naming the discussion + due date + work mode — declining aborts
       before any extraction (FR-005); a gate disabled in config is skipped;
    5. main-post mode extracts ``prompt.md``, runs the main workflow, persists
       ``response.md``, then ``fill_reply`` — never submitting (FR-010);
    6. peer-reply mode extracts ``prompt.md`` + ``peer-posts.md``, runs the peer workflow,
       verifies the two peer-reply files, and stops without writing to the portal;
    7. on ``FillVerifyFailed``/``SelectorMiss`` during main fill: keep ``response.md`` and
       tell the operator to paste it manually (FR-012/FR-015).
    """
    # The context is intentionally NOT closed: main mode leaves the drafted reply sitting
    # unsubmitted in the live field, and peer mode leaves the operator in the same discussion
    # page for manual paste. main() is one-shot, so the OS reaps the browser when the
    # operator closes it / the process exits.
    _context, page = browser_factory()

    _navigate_to_discussions(
        adapter, page, config.target_classes[0],
        ensure_logged_in=ensure_logged_in, announce=announce,
    )
    discussions = adapter.list_discussions(page)
    selected = select_soonest_due(discussions, today)
    if selected is None:
        raise NoUpcomingDiscussion(
            _no_upcoming_message(config.target_classes[0], discussions, today)
        )

    mode = _resolve_mode(config, choose_mode)
    gate_prompt = (
        f"Selected discussion: {selected.title!r} (due {selected.due_date}). "
        f"Work mode: {_MODE_LABELS[mode]}. Proceed? [y/N] "
    )
    if config.confirm and not confirm(gate_prompt):
        announce("Aborted before extraction: confirmation declined.")
        return

    adapter.open_discussion(page, selected)
    prompt_text = adapter.extract_prompt(page)
    run_dir = make_run_dir(config.run_root)
    handoff.write_prompt(
        run_dir,
        prompt_text,
        {"title": selected.title, "due": str(selected.due_date), "url": selected.url},
    )

    if mode == MODE_PEER:
        peer_posts = adapter.extract_peer_posts(page)
        handoff.write_peer_posts(run_dir, peer_posts)
        session(
            run_dir,
            config.editor_cmd,
            template_path=handoff.PEER_REPLIES_WORKFLOW_TEMPLATE,
            require_response=False,
        )
        peer_replies = handoff.read_peer_replies(run_dir)
        announce(
            f"Peer reply drafts ready for {selected.title!r} (due {selected.due_date}). "
            f"Paste them manually from {run_dir / handoff.PEER_REPLY_FILES[0]} and "
            f"{run_dir / handoff.PEER_REPLY_FILES[1]} ({len(peer_replies)} ready)."
        )
        return

    response = session(
        run_dir,
        config.editor_cmd,
        template_path=handoff.WORKFLOW_TEMPLATE,
        require_response=True,
    )
    # FR-015: the final main response is on disk before any write-back is attempted.
    (run_dir / handoff.RESPONSE_FILE).write_text(response, encoding="utf-8")

    try:
        adapter.fill_reply(page, response)
    except (FillVerifyFailed, SelectorMiss) as exc:
        announce(
            f"Reply NOT inserted ({exc}). Your response is preserved at "
            f"{run_dir / handoff.RESPONSE_FILE} — please paste manually."
        )
        return

    announce(
        f"Reply drafted into the field for {selected.title!r} (due {selected.due_date}) — "
        "review it and submit it yourself."
    )


def validate(
    page,
    *,
    adapter,
    confirm=_confirm_via_input,
    fixtures_dir=Path("fixtures"),
    class_id: str = "",
    today: dt.date | None = None,
    ensure_logged_in=browser.ensure_logged_in,
    announce=print,
) -> int:
    """Guided live-check: drive each live step on ``page`` and gate it on a single-keypress
    operator confirmation (FR-017). On a ``SelectorMiss`` the tool snapshots the live DOM to
    ``fixtures_dir/<step>_live.html`` itself (FR-018), names ``portal_adapter.py`` as the
    one-file fix, and stops — the operator never hand-captures markup. Nothing is submitted.

    The first navigation pauses for MANUAL login and retries once if the portal redirects to
    the SSO login (FR-003, Esc#2 — the pause is post-navigation, where the redirect is visible).

    Returns 0 when every checkpoint is confirmed, 1 when a checkpoint is declined or nothing
    is upcoming, 2 when login could not be completed, 3 on a selector miss (a snapshot was
    written). The ``adapter``/``confirm``/``ensure_logged_in``/``announce`` seams are injected
    so the flow logic is unit-testable with fakes; the live page-recognition residue is T026.
    """
    if today is None:
        today = dt.date.today()
    step = "navigate"
    try:
        _navigate_to_discussions(
            adapter, page, class_id, ensure_logged_in=ensure_logged_in, announce=announce
        )
        step = "list"
        discussions = adapter.list_discussions(page)
        selected = select_soonest_due(discussions, today)
        if selected is None:
            announce(_no_upcoming_message(class_id, discussions, today))
            return 1
        if not confirm(f"Found {selected.title!r} due {selected.due_date} — correct? [y] "):
            announce("Guided validation stopped: selection not confirmed.")
            return 1
        step = "extract"
        adapter.open_discussion(page, selected)
        prompt = adapter.extract_prompt(page)
        if not confirm(f"Extracted the prompt ({len(prompt)} chars) — looks right? [y] "):
            announce("Guided validation stopped: prompt not confirmed.")
            return 1
        step = "fill"
        adapter.fill_reply(page, _VALIDATE_SAMPLE)
        if not confirm("Filled the reply field — your text shows, nothing submitted? [y] "):
            announce("Guided validation stopped: fill not confirmed.")
            return 1
    except NotAuthenticated as exc:
        # The login pause + single retry ran and the operator still is not signed in: stop the
        # walk (routed to the pause path, NOT a misleading selector-miss snapshot). Nothing
        # was submitted.
        announce(
            f"Guided validation stopped: not signed in ({exc}). Log in in the browser "
            "window, then re-run `discuss validate`."
        )
        return 2
    except SelectorMiss as exc:
        snapshot = Path(fixtures_dir) / f"{step}_live.html"
        # FR-018: the tool must capture the live markup ITSELF — create the fixtures dir if
        # it is absent (fresh checkout / CWD without fixtures/) so the snapshot never turns
        # into a traceback instead of a capture.
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        snapshot.write_text(page.content(), encoding="utf-8")
        announce(
            f"Selector miss at the {step!r} step: {exc}\n"
            f"Saved the live page markup to {snapshot} for re-capture. Fix the selector in "
            "src/discuss/portal_adapter.py — the one-file home for every portal selector."
        )
        return 3
    announce("Guided validation complete — every checkpoint confirmed; nothing was submitted.")
    return 0


def _run_validate(config: Config) -> int:
    """Wire the real live dependencies for ``discuss validate`` (FR-017): open the operator's
    persistent context, then run the guided walk against the real adapter. The manual-login
    pause is INSIDE the walk, after the first navigation (Esc#2) — there is no pre-navigation
    auth check here. Fails loud (rc 2) with guidance when no class is configured, before any
    browser is opened."""
    if not config.target_classes:
        print(_NO_CLASS_MESSAGE)
        return 2
    _context, page = browser.open_persistent_context(config.profile_dir)
    return validate(
        page,
        adapter=portal_adapter,
        class_id=config.target_classes[0],
        today=dt.date.today(),
    )


def main(argv=None) -> int:
    """Console entry: dispatch ``discuss validate`` to the guided check, else build the real
    dependencies and delegate to ``run`` (FR-001)."""
    args = sys.argv[1:] if argv is None else list(argv)
    config = Config.load(_load_overrides())

    if args and args[0] == "validate":
        return _run_validate(config)

    if not config.target_classes:
        print(_NO_CLASS_MESSAGE)
        return 2

    def browser_factory():
        return browser.open_persistent_context(config.profile_dir)

    try:
        run(
            config=config,
            browser_factory=browser_factory,
            adapter=portal_adapter,
            today=dt.date.today(),
        )
    except DiscussError as exc:
        print(f"discuss: {exc}")
        return 1
    return 0

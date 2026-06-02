"""`discuss` console-script entry point + the orchestrator pipeline (T017).

``run()`` wires the pieces into the one-click flow (FR-001): open the persistent context →
pause for manual login if needed → navigate to the soonest-due discussion → confirm with
the operator → extract the prompt → hand off to a primed session for an operator-edited
draft → inject that draft into the reply field WITHOUT submitting. The adapter, the
session, and the login/confirm/announce seams are all injected so the whole pipeline is
testable with fakes (tests/test_cli_pipeline.py); ``main()`` supplies the real
implementations and is verified end-to-end live in T019.
"""

from __future__ import annotations

import datetime as dt
import os
from pathlib import Path

from discuss import browser, handoff, portal_adapter
from discuss.config import Config
from discuss.errors import DiscussError, FillVerifyFailed, NoUpcomingDiscussion, SelectorMiss
from discuss.portal_parse import select_soonest_due

_FALSEY = {"0", "false", "no", "off"}


def _confirm_via_input(prompt: str) -> bool:
    """Default confirmation gate: ask the operator and accept only an explicit yes."""
    return input(prompt).strip().lower() in ("y", "yes")


def _load_overrides(env=os.environ) -> dict:
    """Gather config overrides from the environment (config.py delegates this to cli).

    Recognised vars (each absent → no key, so the documented default wins):
      DISCUSS_TARGET_CLASSES  comma-separated class ids (e.g. ``_577963_1,_x_2``)
      DISCUSS_EDITOR          a ``--wait``-style editor command (space-separated)
      DISCUSS_PROFILE_DIR     persistent browser profile dir
      DISCUSS_RUN_ROOT        parent dir for per-run working dirs
      DISCUSS_CONFIRM         set to a falsey value (0/false/no/off) to disable the gate
    """
    overrides: dict = {}
    classes = env.get("DISCUSS_TARGET_CLASSES", "").strip()
    if classes:
        overrides["target_classes"] = [c.strip() for c in classes.split(",") if c.strip()]
    editor = env.get("DISCUSS_EDITOR", "").strip()
    if editor:
        overrides["editor_cmd"] = editor.split()
    profile = env.get("DISCUSS_PROFILE_DIR", "").strip()
    if profile:
        overrides["profile_dir"] = Path(profile)
    run_root = env.get("DISCUSS_RUN_ROOT", "").strip()
    if run_root:
        overrides["run_root"] = Path(run_root)
    confirm = env.get("DISCUSS_CONFIRM", "").strip()
    if confirm:
        overrides["confirm"] = confirm.lower() not in _FALSEY
    return overrides


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
    announce=print,
) -> None:
    """Run the full pipeline once. Ordering and safety guarantees, top to bottom:

    1. open the context and ``ensure_logged_in`` (a ``NotAuthenticated`` here surfaces);
    2. navigate + list + ``select_soonest_due`` — ``None`` → ``NoUpcomingDiscussion`` (stop,
       extract nothing) (FR-014);
    3. **confirmation gate** naming the discussion + due date — declining aborts before any
       extraction (FR-005); a gate disabled in config is skipped;
    4. extract the prompt, write ``prompt.md`` (FR-006), hand off to the session for an
       operator-edited ``response.md``;
    5. **persist the confirmed response to disk before write-back** (FR-015), then
       ``fill_reply`` — never submitting (FR-010);
    6. on ``FillVerifyFailed``/``SelectorMiss`` during fill: keep ``response.md`` and tell
       the operator to paste it manually (FR-012/FR-015).
    """
    # The context is intentionally NOT closed: the run ends with the drafted reply sitting
    # unsubmitted in the live field, and the operator finishes in this same browser window —
    # reviewing and submitting the post themselves (P-II/FR-010). main() is one-shot, so the
    # OS reaps the browser when the operator closes it / the process exits.
    _context, page = browser_factory()
    ensure_logged_in(page)  # NotAuthenticated propagates — the run cannot proceed

    adapter.go_to_discussions(page, config.target_classes[0])
    selected = select_soonest_due(adapter.list_discussions(page), today)
    if selected is None:
        raise NoUpcomingDiscussion("no discussion has an upcoming due date")

    gate_prompt = (
        f"Selected discussion: {selected.title!r} (due {selected.due_date}). "
        "Proceed to draft a reply? [y/N] "
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
    response = session(run_dir, config.editor_cmd)
    # FR-015: the final response is on disk before any write-back is attempted.
    (run_dir / handoff.RESPONSE_FILE).write_text(response, encoding="utf-8")

    try:
        adapter.fill_reply(page, response)
    except (FillVerifyFailed, SelectorMiss) as exc:
        announce(
            f"Reply NOT inserted ({exc}). Your response is preserved at "
            f"{run_dir / handoff.RESPONSE_FILE} — please paste it into the reply field "
            "manually."
        )
        return

    announce(
        f"Reply drafted into the field for {selected.title!r} (due {selected.due_date}) — "
        "review it and submit it yourself."
    )


def main() -> int:
    """Console entry: build the real dependencies and delegate to ``run`` (FR-001)."""
    config = Config.load(_load_overrides())
    if not config.target_classes:
        print(
            "discuss: no target class configured. Set DISCUSS_TARGET_CLASSES to one or more "
            "class ids,\n  e.g.  DISCUSS_TARGET_CLASSES=_577963_1 discuss\n"
            "  (find the id in the course URL: .../ultra/courses/<class_id>/...)."
        )
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

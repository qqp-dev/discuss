"""T025 — `discuss validate` guided live-check flow logic (FR-017, FR-018).

The guided walk drives each live step itself and gates every visual checkpoint on a
single-keypress confirm; on a selector miss it self-snapshots the live DOM (FR-018) and
stops, naming `portal_adapter.py` as the one-file fix — the operator never hand-captures
markup. The *flow logic* (single-keypress prompts; decline aborts; miss → snapshot+stop) is
unit-tested here with a fake page + fake adapter + a tmp fixtures dir; the irreducibly-live
run is T026.
"""

import datetime as dt

import pytest

from discuss import cli
from discuss.config import Config
from discuss.errors import NotAuthenticated, SelectorMiss
from discuss.portal_parse import Discussion


# --- fakes: a page whose content() is capturable, an adapter that can miss at a named step -


class _FakePage:
    url = "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"

    def content(self):
        return "<html><body>captured live markup</body></html>"


def fake_page_factory(miss_at=None):
    # models the live page; the miss is driven by the adapter (miss_at is accepted so the
    # call site reads naturally, but the page itself is always a capturable snapshot).
    return _FakePage()


class FakeAdapter:
    """Stand-in for the live portal_adapter, configurable to raise SelectorMiss at a step."""

    def __init__(self, miss=None):
        self.miss = miss
        self.list_calls = 0
        self.filled = False
        self.fill_text = None

    def go_to_discussions(self, page, class_id):
        if self.miss == "navigate":
            raise SelectorMiss("discussions list did not render")

    def list_discussions(self, page):
        self.list_calls += 1
        if self.miss == "list":
            raise SelectorMiss("rows did not resolve")
        return [Discussion(title="Wk 1 Discussion: Critical Thinking",
                           due_date=dt.date(2999, 1, 1), url="u")]

    def open_discussion(self, page, discussion):
        if self.miss == "open":
            raise SelectorMiss("prompt container not found")

    def extract_prompt(self, page):
        if self.miss == "extract":
            raise SelectorMiss("prompt text was empty")
        return "Discuss the assigned prompt in your own words."

    def fill_reply(self, page, text):
        if self.miss == "fill":
            raise SelectorMiss("reply field not found")
        self.filled = True
        self.fill_text = text


def _confirm_first_n(n):
    """A confirm that says yes to the first n checkpoints, then no — to drive declines."""
    calls = {"i": 0}

    def confirm(prompt):
        calls["i"] += 1
        return calls["i"] <= n

    return confirm


# --- the two task-specified tests ------------------------------------------------------


def test_guided_validation_uses_single_keypress_confirms(monkeypatch, tmp_path):
    # FR-017: every checkpoint is a single-keypress confirm; declining stops the walk.
    prompts = []

    def fake_confirm(p):
        prompts.append(p)
        return True

    cli.validate(fake_page_factory(), adapter=FakeAdapter(), confirm=fake_confirm,
                 fixtures_dir=tmp_path)
    assert prompts, "validate must ask the operator to confirm at least one checkpoint"
    assert all("[y]" in p.lower() for p in prompts)             # single-keypress shape


def test_validate_snapshots_dom_on_selector_miss(tmp_path):
    # FR-018: a selector miss self-snapshots the live DOM; operator never hand-captures.
    cli.validate(fake_page_factory(miss_at="extract"), adapter=FakeAdapter(miss="extract"),
                 confirm=lambda p: True, fixtures_dir=tmp_path)
    assert list(tmp_path.glob("*_live.html")), "a selector miss must snapshot the DOM"


# --- added: full branch coverage of the flow logic -------------------------------------


def test_validate_happy_path_walks_and_fills_without_submitting(tmp_path):
    # the clean walk: every checkpoint confirmed → rc 0, the field was filled (never submitted),
    # and the sample text the operator eyeballs was the one handed to fill_reply.
    adapter = FakeAdapter()
    rc = cli.validate(fake_page_factory(), adapter=adapter, confirm=lambda p: True,
                      fixtures_dir=tmp_path, today=dt.date(2026, 6, 1))
    assert rc == 0
    assert adapter.filled is True
    assert adapter.fill_text  # a non-empty sample reply was injected for the operator to see


def test_validate_stops_when_nothing_upcoming(tmp_path):
    # no upcoming discussion → report the same evidence-rich diagnostic as a normal run,
    # stop before any confirm, and never reach a fill.
    adapter = FakeAdapter()
    asked = []
    messages = []
    rc = cli.validate(fake_page_factory(), adapter=adapter,
                      confirm=lambda p: asked.append(p) or True, fixtures_dir=tmp_path,
                      class_id="_577963_1", announce=messages.append,
                      today=dt.date(3000, 1, 1))  # the only discussion (2999) is now past
    assert rc != 0
    assert messages == [
        "No upcoming discussion for class _577963_1. Discussions found: 1. "
        "Discussions with parseable due dates: 1. Parseable due-date range: "
        "2999-01-01 to 2999-01-01. Today: 3000-01-01. Saved the list page markup to "
        f"{tmp_path / cli.LIST_SNAPSHOT_FILE}."
    ]
    assert (tmp_path / cli.LIST_SNAPSHOT_FILE).read_text(encoding="utf-8") == (
        "<html><body>captured live markup</body></html>"
    )
    assert adapter.list_calls == 1
    assert adapter.filled is False
    assert asked == []  # stopped before the first checkpoint


def test_validate_stops_when_selection_declined(tmp_path):
    # decline the FIRST checkpoint (selection) → abort before extract/fill.
    adapter = FakeAdapter()
    rc = cli.validate(fake_page_factory(), adapter=adapter, confirm=_confirm_first_n(0),
                      fixtures_dir=tmp_path)
    assert rc != 0
    assert adapter.filled is False


def test_validate_stops_when_prompt_declined(tmp_path):
    # confirm selection, then decline the prompt checkpoint → never fill.
    adapter = FakeAdapter()
    rc = cli.validate(fake_page_factory(), adapter=adapter, confirm=_confirm_first_n(1),
                      fixtures_dir=tmp_path)
    assert rc != 0
    assert adapter.filled is False


def test_validate_stops_when_fill_declined(tmp_path):
    # confirm selection + prompt, fill happens, then decline the fill checkpoint → rc nonzero.
    adapter = FakeAdapter()
    rc = cli.validate(fake_page_factory(), adapter=adapter, confirm=_confirm_first_n(2),
                      fixtures_dir=tmp_path)
    assert rc != 0
    assert adapter.filled is True  # the fill ran; the operator judged it wrong


def test_validate_snapshots_named_step_on_navigate_miss(tmp_path):
    # a miss at the first step snapshots a file named for THAT step, and reports rc 3.
    rc = cli.validate(fake_page_factory(), adapter=FakeAdapter(miss="navigate"),
                      confirm=lambda p: True, fixtures_dir=tmp_path)
    assert rc == 3
    assert (tmp_path / "navigate_live.html").exists()


def test_validate_self_snapshots_even_when_fixtures_dir_absent(tmp_path):
    # FR-018 robustness: the tool must capture the live markup ITSELF even from a CWD whose
    # fixtures dir does not exist yet — a missing dir must never turn the snapshot into a
    # traceback (it would defeat the "tool self-captures, operator never hand-captures" point).
    target = tmp_path / "not_created_yet"
    rc = cli.validate(fake_page_factory(), adapter=FakeAdapter(miss="navigate"),
                      confirm=lambda p: True, fixtures_dir=target)
    assert rc == 3
    assert (target / "navigate_live.html").exists()


# --- the `discuss validate` dispatch + the live wrapper --------------------------------


def test_main_dispatches_validate_subcommand(monkeypatch):
    # `discuss validate` routes to the validate wrapper (not the draft pipeline).
    seen = {}
    monkeypatch.setattr(cli, "_run_validate", lambda config: seen.setdefault("rc", 0) or 0)
    rc = cli.main(["validate"])
    assert rc == 0
    assert "rc" in seen  # the validate wrapper, not run(), handled it


def test_run_validate_requires_a_target_class(capsys):
    # no class configured → fail loud with guidance, never open a browser.
    rc = cli._run_validate(Config.load({}))
    assert rc == 2
    assert "DISCUSS_TARGET_CLASSES" in capsys.readouterr().out


def test_run_validate_opens_context_and_walks(monkeypatch):
    # the live wrapper opens the PERSISTENT context, then runs the guided walk against the real
    # adapter. Post-Esc#2 there is NO pre-navigation login pause here — the manual-login pause
    # now lives INSIDE the walk, after the first navigation (so it can see the SSO redirect).
    # All live calls stubbed so no browser is touched.
    calls = {}

    def fake_open(profile_dir):
        calls["profile"] = profile_dir
        return ("ctx", "page")

    monkeypatch.setattr(cli.browser, "open_persistent_context", fake_open)
    monkeypatch.setattr(cli.browser, "ensure_logged_in",
                        lambda page: calls.__setitem__("pre_nav_pause", page))

    def fake_validate(page, *, adapter, class_id, **kw):
        calls["validate"] = (page, adapter, class_id)
        return 0

    monkeypatch.setattr(cli, "validate", fake_validate)
    rc = cli._run_validate(Config.load({"target_classes": ["_x_1"]}))
    assert rc == 0
    assert calls["validate"][0] == "page"            # the opened page was walked
    assert calls["validate"][1] is cli.portal_adapter  # against the REAL adapter
    assert calls["validate"][2] == "_x_1"            # for the configured class
    assert "pre_nav_pause" not in calls              # NO auth check before navigation (Esc#2)


def test_validate_reports_not_authenticated(tmp_path):
    # a persistent login landing inside the guided walk: the post-navigation pause + single
    # retry runs, and if login is never resolved the walk stops with a non-zero rc — routed to
    # the pause path, not a crash and not a misleading selector-miss snapshot.
    class _A(FakeAdapter):
        def go_to_discussions(self, page, class_id):
            raise NotAuthenticated("login persisted across the retry")

    adapter = _A()
    rc = cli.validate(fake_page_factory(), adapter=adapter, confirm=lambda p: True,
                      fixtures_dir=tmp_path, ensure_logged_in=lambda page: None)
    assert rc == 2
    assert adapter.filled is False

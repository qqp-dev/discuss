"""Shared pytest fixtures for the discuss test suite.

Fixtures are added by the tasks that need them:
- saved-HTML fixtures (`login_fixture_html`, `discussions_fixture_html`, ...) arrive
  with T006/T010/T011 once T002 has captured real portal markup into `fixtures/`.
- the orchestration `fake_ctx` fixture arrives with T017.

This file exists from T001 so those tasks have a single place to land their fixtures.
"""

from __future__ import annotations

import datetime as dt
import pathlib

import pytest

from discuss import cli, handoff
from discuss.config import Config
from discuss.portal_parse import Discussion, PeerPost

_FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures"


def _read(name: str) -> str:
    return (_FIXTURES / name).read_text(encoding="utf-8")


# --- saved-HTML fixtures captured live in T002 (real UOPX / Blackboard Ultra markup) ---


@pytest.fixture
def login_fixture_html() -> str:
    """The logged-out University of Phoenix login page."""
    return _read("login_page.html")


@pytest.fixture
def discussions_fixture_html() -> str:
    """The logged-in discussions list (7 rows; 5 carry a due date)."""
    return _read("discussions_list.html")


@pytest.fixture
def discussion_page_fixture_html() -> str:
    """A single discussion page whose first prompt container holds the instructor prompt."""
    return _read("discussion_page.html")


@pytest.fixture
def login_shell_prerender_html() -> str:
    """The PRE-RENDER ForgeRock SSO login shell (Esc#2): captured by FR-018 self-snapshot on
    the first live run, the 1.6 KB un-painted Vue shell the live adapter actually reads —
    `<title>Login</title>` + `data-testid="fr-body-image"`, no post-render marker."""
    return _read("login_shell_prerender.html")


# --- URLs that accompany those captures (is_login_page takes both url and html) ---


@pytest.fixture
def login_url() -> str:
    return "https://www.phoenix.edu/login"


@pytest.fixture
def discussions_url() -> str:
    return "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"


# --- orchestration test double + context, used by tests/test_cli_pipeline.py (T017) ---


class FakeAdapter:
    """A recording stand-in for the live portal_adapter (FR-001: adapter is injected).

    Flags let a test assert ordering/safety guarantees without any browser: ``extracted``/
    ``filled`` track which steps ran, ``submitted`` is ALWAYS False (a fake that never
    submits mirrors the real no-submit guarantee), ``response_existed_at_fill`` records
    whether response.md was on disk when fill was attempted (FR-015), and ``fill_raises``
    injects a failure to exercise the abort path.
    """

    def __init__(self, discussions, run_dir, fill_raises=None):
        self.discussions = discussions
        self._run_dir = run_dir
        self.fill_raises = fill_raises
        self.extracted = False
        self.filled = False
        self.submitted = False
        self.response_existed_at_fill = False
        self.peer_posts = [
            PeerPost(index=1, author="Student A", text="A thoughtful classmate post."),
            PeerPost(index=2, author="Student B", text="Another useful classmate post."),
        ]

    def go_to_discussions(self, page, class_id):
        return page

    def list_discussions(self, page):
        return self.discussions

    def open_discussion(self, page, discussion):
        return page

    def extract_prompt(self, page):
        self.extracted = True
        return "Discuss the assigned prompt in your own words."

    def extract_peer_posts(self, page):
        return self.peer_posts

    def fill_reply(self, page, text):
        self.response_existed_at_fill = (self._run_dir / handoff.RESPONSE_FILE).exists()
        if self.fill_raises is not None:
            raise self.fill_raises
        self.filled = True  # never sets submitted — the real fill never submits either


class FakeCtx:
    """Bundles the fakes + injected seams so a test calls ``cli.run(**fake_ctx.kwargs)``."""

    def __init__(self, tmp_path):
        self.run_dir = tmp_path / "run-0001"
        self.run_dir.mkdir()
        self.today = dt.date(2026, 6, 1)
        self.confirm_answer = True
        self.mode = cli.MODE_MAIN
        self.mode_prompted = False
        self.gate_prompt = None
        self.last_message = None
        self.selected = Discussion(
            title="Wk 1 Discussion: Developing Critical Thinking Habits",
            due_date=dt.date(2026, 6, 8),
            url="https://vle.phoenix.edu/ultra/courses/_577963_1/engagement/discussion/_1_1",
        )
        past = Discussion(title="Old", due_date=dt.date(2020, 1, 1), url="u")
        self.adapter = FakeAdapter(discussions=[past, self.selected], run_dir=self.run_dir)
        self.config = Config.load(
            {
                "confirm": True,
                "target_classes": ["_577963_1"],
                "run_root": tmp_path,
                "editor_cmd": ["true"],
            }
        )

    # injected seams ---------------------------------------------------------------
    def _browser_factory(self):
        return (object(), object())  # (context, page) — opaque; the fake adapter ignores them

    def _ensure_logged_in(self, page):
        return page

    def _confirm(self, prompt):
        self.gate_prompt = prompt
        return self.confirm_answer

    def _choose_mode(self):
        self.mode_prompted = True
        return self.mode

    def _announce(self, message):
        self.last_message = message

    def _make_run_dir(self, run_root):
        return self.run_dir

    def _session(self, run_dir, editor_cmd, template_path=None, require_response=True):
        (run_dir / handoff.RESPONSE_FILE).write_text("My edited final answer.\n", encoding="utf-8")
        (run_dir / handoff.PEER_REPLY_FILES[0]).write_text("Peer reply one.\n", encoding="utf-8")
        (run_dir / handoff.PEER_REPLY_FILES[1]).write_text("Peer reply two.\n", encoding="utf-8")
        return "My edited final answer."

    @property
    def kwargs(self):
        return dict(
            config=self.config,
            browser_factory=self._browser_factory,
            adapter=self.adapter,
            today=self.today,
            session=self._session,
            confirm=self._confirm,
            choose_mode=self._choose_mode,
            announce=self._announce,
            ensure_logged_in=self._ensure_logged_in,
            make_run_dir=self._make_run_dir,
        )


@pytest.fixture
def fake_ctx(tmp_path):
    return FakeCtx(tmp_path)

"""Shared pytest fixtures for the discuss test suite.

Fixtures are added by the tasks that need them:
- saved-HTML fixtures (`login_fixture_html`, `discussions_fixture_html`, ...) arrive
  with T006/T010/T011 once T002 has captured real portal markup into `fixtures/`.
- the orchestration `fake_ctx` fixture arrives with T017.

This file exists from T001 so those tasks have a single place to land their fixtures.
"""

from __future__ import annotations

import pathlib

import pytest

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


# --- URLs that accompany those captures (is_login_page takes both url and html) ---


@pytest.fixture
def login_url() -> str:
    return "https://www.phoenix.edu/login"


@pytest.fixture
def discussions_url() -> str:
    return "https://vle.phoenix.edu/ultra/courses/_577963_1/engagement"

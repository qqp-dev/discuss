"""Shared pytest fixtures for the discuss test suite.

Fixtures are added by the tasks that need them:
- saved-HTML fixtures (`login_fixture_html`, `discussions_fixture_html`, ...) arrive
  with T006/T010/T011 once T002 has captured real portal markup into `fixtures/`.
- the orchestration `fake_ctx` fixture arrives with T017.

This file exists from T001 so those tasks have a single place to land their fixtures.
"""

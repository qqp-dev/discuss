"""Typed fail-loud errors (FR-014).

One exception class per fail-loud condition so the orchestrator can stop and report
the *specific* failing step rather than retry-storming or proceeding on a guess. All
inherit `DiscussError`, which carries an operator-facing message.
"""


class DiscussError(Exception):
    """Base for all fail-loud conditions. Carries an operator-facing message."""


class NotAuthenticated(DiscussError):
    """The portal session is logged out / expired; pause for manual login (FR-003)."""


class NoUpcomingDiscussion(DiscussError):
    """No discussion has an upcoming due date; stop rather than pick a past one."""


class SelectorMiss(DiscussError):
    """A captured portal selector did not match; the portal markup likely changed."""


class EmptyResponse(DiscussError):
    """The saved response is missing or whitespace-only; do not write back."""


class FillVerifyFailed(DiscussError):
    """Read-back of the filled reply field did not equal the intended text (FR-012)."""

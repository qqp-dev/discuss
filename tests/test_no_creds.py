"""T023 — structural no-credentials oracle (FR-002, SC-007).

An offline, every-build proof that no module writes a credential or automates a login
form: the only persistent-state path is the operator's own browser profile dir handed to
``launch_persistent_context``. Scans the ``src/discuss`` tree as CODE — docstrings stripped
and comments dropped (``ast.unparse``) — so the safety prose that legitimately mentions
"password"/"credential" cannot false-RED this oracle (G1 caught the earlier bare-word form
red-ing on a "no password field" comment). Falsifiable: a ``page.fill("#password", …)`` or
a secrets-file write reds it.
"""

import ast
import pathlib

SRC = pathlib.Path("src/discuss")


def _code_only(py: pathlib.Path) -> str:
    """Module source as code: docstrings stripped, comments dropped (``ast.unparse``) — so
    the safety prose that mentions 'password'/'credential' cannot false-RED this oracle (G1
    caught the earlier bare-word form red-ing on the 'no password field' comment)."""
    tree = ast.parse(py.read_text())
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (isinstance(body, list) and body and isinstance(body[0], ast.Expr)
                and isinstance(getattr(body[0], "value", None), ast.Constant)
                and isinstance(body[0].value.value, str)):
            node.body = body[1:]                   # drop this scope's docstring
    return ast.unparse(tree).lower()


def test_no_credentials_persisted():
    # FR-002/SC-007: never automate the login form, never store a credential. Scan CODE only,
    # and only for ACTIONABLE patterns (an API call / a real selector / a secrets file) — not
    # the bare words that appear in the modules' safety comments.
    code = "\n".join(_code_only(p) for p in SRC.glob("*.py"))
    for forbidden in ("getpass", "keyring", "#password", "secret=", "credentials.json",
                      "password_field", "login_form", ".fill(pw"):
        assert forbidden not in code, f"a module's CODE references {forbidden!r}"
    # the only persistence is the operator's own browser profile (no stored secret)
    assert "launch_persistent_context" in (SRC / "browser.py").read_text()

"""T021 — structural no-submit oracle (FR-010, SC-007).

An offline, every-build proof of a safety *absence*: the reply-fill code path contains no
submit/post-control lookup or click. It reads the *source* of ``portal_adapter.fill_reply``
and scans the CODE only — the docstring (which legitimately documents the no-submit
guarantee) and comments are stripped first, so the oracle cannot false-RED on the prose
that describes the guarantee (the earlier bare ``"submit" in getsource`` form did exactly
that; G1 caught it). Falsifiable: inject a post-button ``.click()`` and it reds; revert and
it greens.
"""

import ast
import inspect

from discuss import portal_adapter


def _code_without_docstring(fn) -> str:
    """The function as code with its docstring removed and comments dropped, so the oracle
    scans CODE — not the prose that legitimately documents the no-submit guarantee. (The
    earlier ``"submit" in getsource`` form false-RED'd on the docstring; G1 caught it.)"""
    node = ast.parse(inspect.getsource(fn)).body[0]
    body = node.body
    if (body and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)):
        node.body = body[1:]                       # drop the docstring statement
    return ast.unparse(node).lower()               # ast.unparse omits comments entirely


def test_fill_reply_has_no_submit_path():
    # FR-010/SC-007: the fill CODE may not look up or click a submit/post control. A green
    # here certifies the *absence* of every submit path on every build — the guarantee that
    # is the whole reason this tool is permitted to touch the reply field at all.
    code = _code_without_docstring(portal_adapter.fill_reply)
    for forbidden in ("submit", "post-button", "btn_post", "publish", "[type='submit']"):
        assert forbidden not in code, f"fill_reply CODE references {forbidden!r}"
    assert code.count(".click(") <= 1              # the only click focuses the editable field

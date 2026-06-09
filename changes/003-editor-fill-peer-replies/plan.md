# 003 Plan

## Approach

- Change the default editor constant and align tests/docs.
- Keep portal selectors quarantined in `portal_adapter.py`; add peer-post selectors there and
  consume them from pure parsing code.
- Add a pure peer-post parser in `portal_parse.py` so tests use saved portal HTML.
- Make peer replies first-class handoff outputs in `handoff.py`.
- Wire the orchestrator to write `peer-posts.md`, require both peer reply drafts, and keep the
  existing no-submit guarantee.
- Harden Quill fill using visible-field wait, explicit focus/selection, keyboard insertion,
  event dispatch, and read-back verification.

## Risk Notes

- The tool still fills only the main top-level reply automatically. Peer replies are drafted
  and preserved for manual paste so the run does not need to submit the main post or walk nested
  reply editors.
- The saved peer-post fixture is privacy-scrubbed, so tests prove selector shape/count and
  handoff behavior, while live content quality remains operator-reviewed.

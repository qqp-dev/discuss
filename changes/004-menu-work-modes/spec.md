# 004 - menu-work-modes

## Summary

Refactor the live run from an all-in-one drafting pass into an explicit work-mode menu:

- Main-post mode drafts/edits `response.md` and fills only the top-level reply field.
- Peer-reply mode drafts/edits `peer-reply-1.md` and `peer-reply-2.md` and stops for manual
  paste.
- `DISCUSS_MODE=main|peer` may skip the menu for shortcuts/tests.

## Acceptance Criteria

- **FR-001**: A run MUST ask whether the operator wants the main post or two classmate replies
  unless `DISCUSS_MODE` pins the mode.
- **FR-002**: Main-post mode MUST require `response.md`, persist it before fill, and MUST NOT
  require peer-reply files.
- **FR-003**: Peer-reply mode MUST extract `peer-posts.md`, require both peer-reply files, and
  MUST NOT fill or submit anything in the portal.
- **FR-004**: The Claude workflow templates MUST be mode-specific and open only the selected
  mode's drafts in the blocking GUI editor.
- **FR-005**: README, contract, constitution, launcher text, and changelog MUST describe the
  menu-mode behavior.

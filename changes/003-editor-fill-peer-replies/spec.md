# 003 - editor-fill-peer-replies

## Summary

Fix the live run ergonomics reported by the operator:

- Use the Linux Mint Cinnamon stock text editor (`xed --wait`) by default.
- Harden rich-text reply insertion so the Blackboard/Quill box is visibly focused and the
  inserted text is verified from the rendered editor.
- Extend the drafting handoff to cover the two required classmate replies by extracting
  visible peer posts, selecting two good candidates, and producing two editable reply drafts.

## Acceptance Criteria

- **FR-001**: The default editor command MUST be `xed --wait`.
- **FR-002**: The main reply fill MUST wait for a visible field, focus it, insert text, and
  verify read-back without clicking any submit/post control.
- **FR-003**: The run MUST extract visible classmate posts from the opened discussion page into
  `peer-posts.md`.
- **FR-004**: The drafting session MUST produce `peer-reply-1.md` and `peer-reply-2.md`; if
  either is missing or blank, the run MUST stop before filling the portal field.
- **FR-005**: The contract, README, launcher description, and workflow template MUST describe
  the new editor default and peer-reply draft behavior.

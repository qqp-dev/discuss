change: 003
impact:
  - section: "Overview & purpose"
    kind: modified
    note: Describes extraction of visible classmate posts, drafting of the main response plus two peer replies, and peer replies as saved drafts for manual paste.
  - section: "The pipeline"
    kind: modified
    note: Adds extraction of peer posts into peer-posts.md alongside prompt.md.
  - section: "Draft handoff"
    kind: modified
    note: Adds peer-post evaluation, selection of two candidates, two shorter peer-reply drafts, and the xed --wait default editor.
  - section: "Reply fill (no submit)"
    kind: modified
    note: Clarifies that automatic fill targets the top-level main reply and peer replies remain draft files for manual paste.
  - section: "Config & run-dir management"
    kind: modified
    note: Changes the default editor to xed --wait and adds peer-posts.md plus peer-reply-1.md / peer-reply-2.md to the run directory contract.
rationale: >
  Change 003 alters operator-visible behavior: it fixes the default editor, hardens main-post
  insertion, and adds first-class peer-reply drafting. The contract sections above are the
  sections that describe those user-visible behaviors and their persisted artifacts.

# 003 Learnings

- Mint's stock editor is `xed`; its `--wait` option is present locally and matches the
  handoff's blocking-editor requirement better than VS Code or terminal-editor examples.
- Blackboard/Quill focus needs to be treated as an observed browser state, not assumed from a
  successful click. The safer path waits for visibility, focuses/selects inside the page, then
  verifies rendered text.
- Peer replies are useful as first-class draft artifacts before automating nested reply editors.
  This keeps the no-submit invariant simple while still covering the two required classmate
  responses in the drafting workflow.

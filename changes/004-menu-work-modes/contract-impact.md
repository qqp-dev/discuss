change: 004
impact:
  - section: "Overview & purpose"
    kind: modified
    note: Describes the new main-post vs peer-reply menu and the distinct mode outcomes.
  - section: "The pipeline"
    kind: modified
    note: Adds the mode menu and changes extraction/handoff/fill to be mode-specific.
  - section: "Draft handoff"
    kind: modified
    note: Splits the Claude workflow into main-post and peer-reply templates with separate required outputs.
  - section: "Reply fill (no submit)"
    kind: modified
    note: Clarifies that only main-post mode fills the portal; peer mode saves drafts for manual paste.
  - section: "Config & run-dir management"
    kind: modified
    note: Adds optional mode config and describes mode-specific run-dir artifacts.
rationale: >
  Change 004 changes the operator-visible flow from one all-in-one pass to two focused work
  modes. The impacted contract sections are the ones that define the run sequence, handoff
  files, fill behavior, and operator-tunable configuration.

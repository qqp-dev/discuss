change: 001
impact:
  - section: "The pipeline"
    kind: added
    note: Created — the fixed run sequence (trigger → persistent browser → navigate click-path → wait-for-render → classify → manual-login pause → select soonest-due → confirm gate → extract prompt). Covers FR-001/004/005/006.
  - section: "Draft handoff"
    kind: added
    note: Created — hand the prompt to a primed interactive Claude Code session that draws out the operator's stance and grounds the draft, then opens a mandatory GUI editor. Covers FR-007/008/009.
  - section: "Reply fill (no submit)"
    kind: added
    note: Created — runtime field-type detection, fill, read-back verify, never submit; abort+preserve+manual-paste on mismatch. Covers FR-010/011/012.
  - section: "Safety invariants"
    kind: added
    note: Created — no-submit (P-II), no credentials persisted (P-I), persist-before-fill (FR-015), human pace / no retry-storm (FR-014/016). Maps to P-I..P-IV.
  - section: "Auth & render handling"
    kind: added
    note: Created — persistent session reuse without re-2FA (FR-002), pre-render login-shell classification, post-navigation manual-login pause with one retry (FR-003), condition-based bounded render wait (FR-004), tool-driven validation (FR-017).
  - section: "Portal-coupling quarantine"
    kind: added
    note: Created — every selector + click-path confined to one adapter module; post-render self-snapshot on selector miss (FR-013/018, P-III).
  - section: "Config & run-dir management"
    kind: added
    note: Created — Config.load knobs (profile/classes/confirm/editor/run-root), per-run dir holding prompt.md/CLAUDE.md/response.md, durable handoff (FR-015).
  - section: "Adapters"
    kind: added
    note: Created — the how bindings 001 introduced — Playwright persistent profile, Claude Code cwd-CLAUDE.md priming, GUI editor, desktop launcher (FR-001).
rationale: >
  Change 001 is the genesis of the whole `discuss` tool — every behavior the contract now
  describes was created by 001's diff (the live-verified navigate → extract → draft-handoff →
  fill-no-submit pipeline and its safety/auth/quarantine guarantees). Because the contract did
  not exist when 001 shipped (its contract-collapse was recorded N/A), 001 is collapsed
  retroactively here: each behavioral contract.md section is `added` by 001, and the contract
  was authored to describe 001's shipped behavior (FR-001..018 / spec §4.2). This is a non-empty
  impact list — never `none` — because 001 changed real, acceptance-asserted behavior. The
  Overview and Methodology & Contract-Loop status sections are change 002's framing of the loop
  itself, declared in 002's own contract-impact.md, not here.

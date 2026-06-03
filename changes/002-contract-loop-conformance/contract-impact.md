change: 002
impact:
  - section: "Overview & purpose"
    kind: added
    note: Created — the contract's opening declaration that this contract.md is the single source of truth, never subordinate to the archive (I1–I3); the framing 002's adoption establishes.
  - section: "Methodology & Contract-Loop status"
    kind: added
    note: Created — declares discuss a conforming instance of portable-core's Contract Loop (schema adopted by copy), the per-change contract-impact.md, collapse-at-archive, and the contract-currency G3 currency gate.
rationale: >
  Change 002 is the conformance adoption: it creates contract.md as an artifact and makes
  `discuss` a conforming instance of the Contract Loop. Its own contract impact is therefore the
  two sections that describe what 002 itself made true — the source-of-truth Overview framing and
  the Methodology & Contract-Loop status section. The behavioral sections (The pipeline, Draft
  handoff, Reply fill, Safety invariants, Auth & render handling, Portal-coupling quarantine,
  Config & run-dir management, Adapters) describe change 001's shipped behavior and are declared
  in 001's contract-impact.md (the retroactive collapse), not here — resolving the genesis
  circularity: the contract 002 creates also documents that 002 created it, without double-counting
  001's behavior. The constitution §7 amendment and CHANGELOG seeding are change-package / archive
  members, not contract.md sections, so they carry no contract-section impact.

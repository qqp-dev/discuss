---
name: tasks
purpose: Executable task breakdown
author: design agent
phase: tasks
---

# Tasks: `<feature-name>`

**Status:** v1
**Date:** YYYY-MM-DD
**Companion to:** `spec.md` and `plan.md`

**Input**: `changes/NNN-<feature-name>/{spec.md, plan.md}`.

**Prerequisites**: spec.md ✓, plan.md ✓.

**Organization**: tasks are grouped by user story so each story can be implemented and
tested independently. Every implementation task ships with an explicit `### Tests` block
— the test plan, not a suggestion.

## Format

- Task headers: `### T<id> [markers] [depends: …] — description`.
- Markers: `[P]` parallelizable · `[TDD]` RED-GREEN-REFACTOR · `[REVIEW]` G2 before
  consumers · `[no-review]` skips the G2 chunk gate (trivially mechanical — no
  behavioral judgment) · `[US1..]` which user story the task serves ·
  `[SETUP]/[FOUND]/[POLISH]` phase.
- Include exact file paths in `**Files touched:**`.

## Per-task acceptance criteria (EARS) and the G2 chunk-review gate

Each task that adds or changes **production code** carries at least one acceptance
criterion written in EARS (Ubiquitous / Event / State / Unwanted / Optional), mapped to
a test id or an explicit `[no-oracle]` marker, in an `ears` fenced block in the task
body — so the **G2** chunk-review gate (`independent-review`, light panel) has a
per-task anchor:

```ears
WHEN <trigger>, the <system> SHALL <observable response>. [test: <test-id>]
```

**G2 firing rule (spec 015):** at each task checkpoint the execute role dispatches the
light G2 panel (`spec-match` for that task + `quality`) **iff** the task touches
production code (a changed path **outside** the constitution §1 coverage-exempt content
globs) **and** is not marked `[no-review]`. Docs/config/scaffold tasks and `[no-review]`
tasks skip G2.

---

## Phase 1 — Setup (shared infrastructure)

**Purpose**: project initialization and structure no story can begin without.

### T001 [SETUP] — `<task title>`

**Files touched:** Create `<path>`.

**Expected behavior:** `<concrete description>`.

- [ ] **T001** — `<action>`.

### Tests
- (setup/scaffold) covered downstream by the story that consumes it.

**Acceptance criterion:** `<concrete observable>`.

---

## Phase 2 — Foundational (blocking prerequisites)

> **⚠️ CRITICAL**: no user-story work begins until this phase completes.

### T002 [FOUND] [TDD] — `<task title>`

**Files touched:** Create `<path>`.

**Expected behavior:** `<concrete description>`.

- [ ] **T002 — RED → GREEN → REFACTOR**
  - RED: write the failing test in `<test path>`; watch it fail correctly.
  - GREEN: minimal code to pass.
  - REFACTOR: clean up; stay green.

### Tests
- **Unit:** `test_<name>` — covers `<behavior>` (falsifiable: removing the behavior reds it).
- **Edge cases:** `<list>`.
- **Non-goals for testing:** `<exclusions>`.

```ears
WHEN <trigger>, the <system> SHALL <observable response>. [test: test_<name>]
```

**Acceptance criterion:** `<concrete observable>`.

---

## Phase 3 — User Story 1 — [Brief title] (Priority: P1) 🎯 MVP

**Goal**: [what this story delivers].

**Independent Test**: [how to verify this story works on its own].

### T003 [US1] [TDD] [depends: T002] — `<task title>`

**Files touched:** Create/Modify `<path>`.

**Expected behavior (FR-00X):** `<concrete description>`.

- [ ] **T003 — RED → GREEN → REFACTOR**
  - RED: failing test first.
  - GREEN: minimal implementation.

### Tests
- **Unit/integration:** `test_<name>` — covers `<behavior>`.
- **Edge cases:** `<list>`.

```ears
IF <unwanted condition>, THEN the <system> SHALL <response>. [test: test_<name>]
```

**Acceptance criterion:** `<observable>`; **[REVIEW] gate (G2)** fires (production code).

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4 — User Story 2 — [Brief title] (Priority: P2)

**Goal**: [what this story delivers].

**Independent Test**: [how to verify this story works on its own].

### T004 [US2] [depends: T002] — `<task title>`

**Files touched:** Modify `<path>`.

**Expected behavior (FR-00Y):** `<concrete description>`.

- [ ] **T004** — `<action>`.

### Tests
- (content/config) `<oracle>`.

**Acceptance criterion:** `<observable>`.

**Checkpoint**: User Stories 1 AND 2 both work independently.

---

[Add more user-story phases as needed, following the same pattern.]

---

## Phase N — Polish & cross-cutting

### TNNN [POLISH] [P] [no-review] — `<task title>`

**Files touched:** Modify `<path>`.

**Expected behavior:** documentation / cleanup / cross-story concerns.

- [ ] **TNNN** — `<action>`.

### Tests
- **Aggregate:** suite + lints green.

**Acceptance criterion:** `<observable>`.

---

## Dependencies & execution order

- **Setup (Phase 1)** → no dependencies; start immediately.
- **Foundational (Phase 2)** → depends on Setup; **blocks all user stories**.
- **User stories (Phase 3+)** → each depends on Foundational; then proceed in priority
  order (P1 → P2 → …) or in parallel where `[P]`/independent.
- **Polish (final)** → depends on the desired user stories being complete.

Within each story: tests RED-first before implementation; respect every `[depends: …]`
marker; commit after each task whose tests pass (and after the G2 gate clears for
`[REVIEW]` tasks). **One checkbox per task** is the resumable handoff state — the
RED/GREEN/REFACTOR rhythm is the `test-driven-development` skill's discipline, tracked
at task granularity, not as three separate checkboxes. On a cold resume the per-task
checkbox state alone answers which task is done / in progress.

## Review Log

> Append-only. Execute appends one row per gate verdict (G2/G3) as it runs — never
> re-edit a task body with verdict prose, and never re-edit a prior row. The single
> per-task checkbox above is the completion state; this log is the verdict trail.
> Empty until execution begins.

| Gate | Anchor | Verdict | Key findings |
|------|--------|---------|--------------|

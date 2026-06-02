---
name: spec
purpose: Feature specification
author: design agent
phase: specify
---

# Spec: `<feature-name>`

**Status:** Draft
**Date:** YYYY-MM-DD
**Author:** design agent

> Authored under change/diff semantics — created by hand (or scaffolded by
> `new-change.sh`) in `changes/NNN-<feature-name>/`. The canonical conventions below
> are methodology, carried by this template; fill them in, delete the guidance.

## 0. Reader's Guide

[Brief roadmap of this document — what a cold reader should read first.]

## 1. Vision & Goals

### 1.1 The problem
[What problem does this feature solve? Why now?]

### 1.2 The goal
[What will exist when complete?]

### 1.3 Success criteria
1. [Verifiable condition]

### 1.4 Non-goals
- [Explicit exclusion — what this change deliberately does not do.]

## 2. User Scenarios & Testing *(mandatory)*

<!--
  User stories are PRIORITIZED user journeys, ordered by importance. Each must be
  INDEPENDENTLY TESTABLE — if you implement just ONE, you still have a viable MVP that
  delivers value. Assign priorities (P1, P2, P3, …); P1 is the most critical. Think of
  each story as a standalone slice that can be developed, tested, and demonstrated on
  its own.
-->

### User Story 1 — [Brief title] (Priority: P1)

[Describe this user journey in plain language — who, doing what, to what end.]

**Why this priority**: [The value, and why it ranks here. P1 is the MVP slice.]

**Independent Test**: [How this story can be verified on its own — e.g. "Can be fully
tested by <action> and delivers <value>."]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome].
2. **Given** [initial state], **When** [action], **Then** [expected outcome].

---

### User Story 2 — [Brief title] (Priority: P2)

[Describe this user journey in plain language.]

**Why this priority**: [The value, and why it ranks below P1. Builds on US1.]

**Independent Test**: [How this story can be verified on its own.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome].

---

[Add more user stories as needed, each with an assigned priority.]

### Edge Cases

- What happens at [boundary condition]?
- How does the system handle [error scenario]?

## 3. Requirements *(mandatory)*

### 3.1 Functional Requirements

<!--
  Number requirements FR-001, FR-002, … and state each as a testable MUST. Mark genuine
  unknowns inline: "[NEEDS CLARIFICATION: <question>]".
-->

- **FR-001**: The `<system>` MUST [specific capability — e.g. "allocate the next
  `changes/NNN-slug/`"].
- **FR-002**: The `<system>` MUST [specific capability].
- **FR-003**: Users MUST be able to [key interaction].
- **FR-004**: The `<system>` MUST [data/state requirement].

### 3.2 Key Entities *(include if the feature involves data)*

- **[Entity 1]**: [What it represents; key attributes, no implementation detail.]
- **[Entity 2]**: [What it represents; relationships to other entities.]

## 4. Success Criteria *(mandatory)*

### 4.1 Measurable Outcomes

<!-- Technology-agnostic and measurable. -->

- **SC-001**: [Measurable outcome — e.g. "A change runs scaffold → spec/plan/tasks → G1
  all-clear with zero <retired-tool> invocations."]
- **SC-002**: [Measurable outcome.]

### 4.2 Acceptance Criteria (EARS)

Write the acceptance criteria the review gates judge against in one of the five **EARS**
shapes — Ubiquitous (`The <system> SHALL …`), Event (`WHEN … SHALL …`), State
(`WHILE … SHALL …`), Unwanted (`IF … THEN … SHALL …`), Optional (`WHERE … SHALL …`) —
each mapped to a test id **or** an explicit `[no-oracle]` marker, inside an `ears`
fenced block. The deterministic EARS floor (`lint-ears.sh`) and the G1 `testability`
reviewer validate these; they are the anchor the independent gates (G1/G2/G3) judge
against:

```ears
WHEN <trigger>, the <system> SHALL <observable response>. [test: <test-id>]
IF <unwanted condition>, THEN the <system> SHALL <response>. [test: <test-id>]
The <system> SHALL <ubiquitous property that has no automatable test>. [no-oracle]
```

## 5. Assumptions

<!-- Reasonable defaults chosen where the description left details open. -->

- [Assumption about scope, environment, or a dependency on an existing system.]

## 6. Dependencies

- [Prior change / system this one stacks on or relies upon.]

## 7. Glossary

- **`<Term>`:** `<Definition>`

## 8. Document History

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.1 | YYYY-MM-DD | design agent | Initial spec. |

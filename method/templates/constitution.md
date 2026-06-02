# Constitution: `<project-name>`

**Project:** `<project-name>`
**Status:** v1
**Last updated:** YYYY-MM-DD

This constitution declares project policy. Discipline-gate skills read it; the planner negotiates changes here, never inline in tasks.

---

## 1. Testing policy

```yaml
coverage_threshold:
  line: 85
  branch: 75

coverage_exemptions: []

mutation_testing: false
```

**Justification for defaults.** Add exemptions as needed (e.g., markdown artifacts, shell scripts tested via smoke tests). Each exemption must have a written justification.

---

## 2. Testing principles

```yaml
testing_principles:
  - per-test-comment-required
  - no-mock-the-system-under-test
  - prefer-controlled-real-boundaries
```

---

## 3. Memory policy

Memory is intentionally out of scope for portable-core v4. The constitution
carries no memory configuration. If you wire a memory layer (gbrain, a vector
DB, in-house code, anything) on top of the workflow artifacts, that layer
carries its own configuration outside this file.

---

## 4. Learning-discipline policy

```yaml
learning_discipline:
  min_section_words: 15
  weasel_words:
    - "be more careful"
    - "in general"
    - "as always"
    - "as expected"
    - "no surprises"
    - "smooth sailing"
    - "all went well"
  enforce_builder_perspective_informs_lesson: true
```

---

## 5. Justifications log

(Empty. Append entries here when loosening any of the above thresholds, with date and rationale.)

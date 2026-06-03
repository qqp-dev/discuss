---
name: contract
purpose: The single current-truth description of what `discuss` does and why. The contract is the source of truth; the implementation is its regenerable projection and the archive (git history + CHANGELOG.md) records how it got here.
author: the discuss project; a conforming instance of portable-core's Contract Loop (method/schemas/contract.md), adopted by copy.
phase: substrate (current truth) / process (collapsed at each change's archive)
---

# Contract: `discuss`

## 1. Overview & purpose

This `contract.md` is the single **source of truth** for what `discuss` does and why; the
implementation under `src/` is its regenerable projection, and the archive (the git commit
history + `CHANGELOG.md` + the retired `changes/NNN/` packages) records how it got here — the
contract is **never subordinate to the archive**. A cold reader can learn the whole behavior
of `discuss` from this file alone, without reading the source or the archive.

`discuss` is a **single-operator local tool**. On one trigger it drives the operator's
already-logged-in University of Phoenix (UOPX / Blackboard Ultra) student-portal session,
finds the discussion with the soonest upcoming due date, extracts its prompt, hands that
prompt to an interactive Claude Code session that helps the operator reason through the
topic and draft a reply in *their own* words, opens that draft in a GUI editor for final
edits, and fills the result into the portal's reply form — **stopping before submit**. The
operator reviews and posts.

The *why* is the governing distinction: `discuss` **assists** the operator's own work; it
does **not** ghostwrite-and-submit. It draws out the operator's stance and evidence, makes
the editor step mandatory, and never clicks the post control. It is a respectful guest on a
portal it does not own — reusing a live human session, never storing credentials, acting at
human pace, and stopping-and-reporting on failure rather than hammering.

## 2. The pipeline

One run is a fixed sequence; each stage is human-paced and touches the minimum number of
pages the click-path requires.

```text
trigger → persistent browser → navigate fixed click-path → wait-for-render →
classify landing → (manual-login pause, post-nav) → select soonest-due →
confirm gate → extract prompt → draft handoff → fill reply (no submit)
```

- **Trigger.** A single operator action launches the run: a desktop launcher
  (`launcher/discuss.desktop` → `launcher/launch.sh`) and an equivalent `discuss`
  console-script both start the orchestrator and open a terminal for the interactive
  session. *(FR-001)*
- **Persistent browser.** The run opens a tool-owned **persistent** browser profile (default
  `./profile/`, gitignored) that reuses the operator's existing authenticated session. *(FR-002;
  see §6 Auth & render handling.)*
- **Navigate the fixed click-path & wait for render.** The tool walks the fixed click-path
  (class → discussions). Because the portal is a client-rendered SPA, the tool **waits for the
  discussions content to render** (discussion rows *or* the login marker) within a bounded,
  human-paced timeout before reading the DOM — it never reads or snapshots a pre-render shell.
  *(FR-004)*
- **Classify the landing.** The rendered (or pre-render login-shell) markup is classified as
  either the discussions list or the SSO login screen. A navigation that redirects to login
  triggers the manual-login pause (§6); it is never mistaken for a selector miss. *(FR-003/FR-004)*
- **Select the soonest-due discussion.** Among the discussions in the configured class(es),
  the tool selects the one with the **soonest upcoming due date**. A past-due or
  unparseable-due discussion is never selected; on a tie the tiebreak is earliest-due then
  listing order, surfaced in the confirmation gate. If nothing is upcoming, the run stops and
  reports rather than guessing. *(FR-004; §5 Safety invariants)*
- **Confirmation gate.** Before extracting, the tool presents a confirmation gate naming the
  selected discussion and its due date. The gate is **on by default** and configurable off; if
  the operator declines, the run aborts cleanly without extracting anything. *(FR-005)*
- **Extract the prompt.** On confirm, the tool extracts the plaintext discussion prompt into
  the run dir (`prompt.md`). *(FR-006)*
- **Draft handoff** → §3. **Fill reply (no submit)** → §4.

## 3. Draft handoff

The extracted prompt is handed to an **interactive Claude Code session**, primed via a
workflow `CLAUDE.md` (rendered into the run dir from `templates/workflow-CLAUDE.md`) with the
reason-with-operator → draft → edit workflow. *(FR-007)*

The primed session **surfaces the prompt's key angles and tensions**, draws out the operator's
stance, points, and any reading/evidence, and **grounds the draft in that input** before
opening the editor. It MUST NOT silently auto-generate a response without operator input —
the human reasons; the tool assists. *(FR-008)*

The session then **opens the draft in a GUI editor** (a `--wait`-capable command; default
`code --wait`, configurable) and **blocks until the operator saves and closes**. The saved
file is the final response. The editor step is mandatory and never skipped. *(FR-009)*

## 4. Reply fill (no submit)

Given the final response and the target discussion page still open, the tool fills the reply
form and stops short of posting.

- **Runtime field-type detection.** The tool detects whether the reply field is a plain
  textarea or a rich-text / contenteditable editor **at runtime** and handles both; the type
  is never hard-coded. *(FR-011)*
- **Fill, then read-back verify.** After filling, the tool **reads the field's rendered content
  back** and compares it to the intended text — an action is verified by its observed effect,
  never by trusting that the call returned (P-IV). *(FR-010/FR-012)*
- **No submit.** No run path ever locates or clicks a submit/post control; the reply is left
  filled and unsubmitted for the operator to review and post. *(FR-010; §5)*
- **On mismatch, abort and preserve.** If the reply field cannot be located, or the read-back
  does not equal the intended text, write-back **aborts**, the response file is **preserved**
  on disk, and the operator is told to **paste manually**. *(FR-012)*

## 5. Safety invariants

These are governance-level guarantees (constitution §6, P-I..P-IV). A run that would violate
one stops instead.

- **No submit (P-II).** The tool fills the reply form and stops; it never auto-submits. The
  operator always performs the final post. *(FR-010)*
- **No credentials persisted (P-I).** The tool reuses the operator's live, human-authenticated
  session; it writes **no** portal credential to disk and touches only the persistent profile
  directory for session state. *(FR-002)*
- **Persist the response before fill (FR-015).** The final response is always written to the
  run dir before any write-back is attempted, so it is never lost if a downstream step fails.
- **Human pace, no retry-storm (P-I).** A run acts at human pace and touches the minimum number
  of pages required by the fixed click-path. On any failure (logged out, nothing due, selector
  miss, empty draft, read-back mismatch) the tool **stops and reports the specific failing
  step** — it never retry-storms or proceeds on a guess. At most **one** bounded, human-paced
  retry is permitted on a transient page-load timeout. *(FR-014/FR-016)*

## 6. Auth & render handling

- **Persistent session reuse.** The operator logs into the portal **by hand once** in the
  tool's persistent profile and chooses "keep me signed in" / "trust this device" when offered.
  The persistent profile then carries the operator's SSO / trusted-device session **across
  launches**: a subsequent run within the session's validity window reaches the discussions
  list **without a fresh manual login and without repeating two-step verification**. If the
  session genuinely cannot persist across launches (forcing re-2FA every run), that is a
  **blocking live finding**, surfaced — never folded into "done". *(FR-002)*
- **Login classification from the pre-render shell.** The SSO login shell (ForgeRock) is a
  client-rendered SPA whose pre-render markup carries none of the post-render discussion
  markers; login is classified from that pre-render shell, never mistaken for a selector miss.
- **Post-navigation manual-login pause with one retry.** The auth check runs **after the first
  portal navigation** (where a login redirect is observable), never against the pre-navigation
  blank page. If a navigation lands on login, the tool **pauses and prompts for manual login in
  the same browser context**, then **retries the navigation once** and continues. It never
  automates credential entry. *(FR-003)*
- **Condition-based bounded wait.** Navigation waits for the rendered content (discussion rows
  or the login marker) within a bounded, human-paced timeout before classifying; it never reads
  the DOM pre-render. *(FR-004)*
- **Tool-driven, in-tool validation.** All human-facing setup and live validation are
  tool-driven: the tool performs each live step and the operator confirms with a single keypress
  at the visual checkpoint. The operator runs no throwaway capture scripts, hand-saves no
  fixtures, and inspects no devtools — the only irreducible manual acts are the one-time
  by-hand login and eyeballing a single guided `discuss validate` run. *(FR-017)*

## 7. Portal-coupling quarantine

Every UOPX-specific selector and the entire click-path live in **one adapter module**
(`src/discuss/portal_adapter.py`); no portal selector appears anywhere else. A portal markup
change is therefore a **one-file fix**. *(FR-013, P-III)* Pure parsing/selection logic
(due-date → target choice, prompt-text extraction from an HTML string) is factored into a
separate, fully-tested `src/discuss/portal_parse.py` that operates on HTML/text strings and is
not coverage-exempt.

When a selector fails to match the live portal, the tool **snapshots the current page markup to
a fixture file itself** (for re-capture and offline re-verification) and reports which step
failed, naming the adapter as the one-file fix — the operator never hand-captures markup. The
snapshot is taken **after** the page has rendered (post-wait), so the diagnostic captures the
rendered DOM rather than an un-rendered SPA shell. *(FR-018)*

## 8. Config & run-dir management

- **Config.** Operator-tunable knobs resolve through `Config.load(overrides)`
  (`src/discuss/config.py`), which merges overrides over documented defaults and ignores
  unknown keys so a stale entry never crashes a run: `profile_dir` (persistent profile,
  default `./profile/`), `target_classes` (the class identifier(s) to search), `confirm` (the
  confirmation gate, default **on**), `editor_cmd` (the `--wait`-capable editor, default `code
  --wait`), and `run_root` (parent of the per-run dirs, default `./runs/`).
- **Run dir.** Each invocation owns a per-run directory holding the extracted `prompt.md`, the
  rendered workflow `CLAUDE.md`, and `response.md` (the final text), plus the selected
  discussion's title, due date, and URL.
- **Durable handoff.** The final response is persisted to the run dir before write-back and
  preserved there on any downstream failure (§5), so the operator's work is never lost.

## 9. Adapters

These are the *how* bindings; the *what* is everything above.

- **Playwright persistent profile** — the tool-owned browser driving the live portal under a
  persistent profile that reuses the operator's session (`src/discuss/browser.py`).
- **Claude Code cwd-`CLAUDE.md` priming** — the draft handoff runs an interactive Claude Code
  session primed by a workflow `CLAUDE.md` rendered into the run dir from
  `templates/workflow-CLAUDE.md`.
- **GUI editor** — a `--wait`-capable editor command (default `code --wait`, configurable) that
  blocks until the operator saves and closes.
- **Desktop launcher** — `launcher/discuss.desktop` + `launcher/launch.sh` provide the
  single-click trigger; the `discuss` console-script is the equivalent CLI entry.

## 10. Methodology & Contract-Loop status

`discuss` is a **conforming instance** of portable-core's **Contract Loop**
(`method/schemas/contract.md`, adopted **by copy** — no runtime link to portable-core). This
`contract.md` is the single current truth; the implementation is its regenerable projection.

- **Change packages** stay physically separate under `changes/NNN-slug/` until archive; each
  carries a `contract-impact.md` at done (`method/schemas/contract-impact.md`).
- **Collapse at archive** updates exactly the declared `contract.md` sections to current truth,
  leaving the archive intact.
- **Currency gate (G3).** A change is not *done* while this contract is stale with respect to
  it: the independent `contract-currency` reviewer gates the G3 done panel (B1 staleness / B2
  mis-declaration), reading `(diff, the change's EARS criteria, contract excerpt, declaration)`.
- **Archive.** The lossless git history + the human-readable `CHANGELOG.md` + the retired change
  packages.
- **Coverage policy** (thresholds and exemptions) lives in `constitution.md` §1; the project
  principles P-I..P-IV that §5/§7 realize live in `constitution.md` §6.

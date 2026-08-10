# Weekly assignment loop

Each UOPX week, the operator posts one **main discussion post** and replies
to **two classmates**. This page is the repeatable loop for doing that with
Claude's help — assisted drafting, draft-only, human review before posting.

## The loop

1. **Trigger the week.** Run `discuss` (or click the Discuss launcher). It
   opens the already-logged-in portal, navigates to the soonest-due
   discussion, and shows the menu: draft/fill the **main post**, or draft the
   **two classmate replies**. You can also just paste this week's prompt into
   a chat.
2. **Draft with Claude.** In a qq-linked Pi session in this Repository,
   invoke the weekly template:
   `/prompts/weekly-assignment` (lives at `.pi/prompts/weekly-assignment.md`).
   Claude asks for your stance and evidence, drafts the main post, then drafts
   the two replies once you paste the classmates' posts.
3. **Review and edit (mandatory).** Open each draft in your editor
   (`DISCUSS_EDITOR`, default `xed --wait`). Claude's drafts are starting
   points — make them yours.
4. **Post manually.** Main-post mode can fill the portal's reply field and
   **stops there**. Peer replies are saved for you to paste manually under
   the specific classmates' posts. The tool never submits; neither should
   Claude.
5. **File the week.** Drafts save under `weeks/<date>-<week-or-topic>/`
   (`prompt.md`, `main-post.md`, `replies.md`) so there's a growing archive of
   the work and the operator's voice.

## Boundaries (ratified in `intent.md`)

- Never auto-submit — no run path locates or clicks a submit control.
- Never stores or types credentials — the operator logs in by hand.
- Human review is mandatory — the editor step is required.
- Human pace — no automated hammering of the portal.

## Where things live

| Thing | Path |
| --- | --- |
| Single source of truth | `intent.md` |
| Portal adapter (one-file fixes) | `src/` (see `docs/SELECTOR-CAPTURE.md`) |
| Weekly drafts | `weeks/` (tracked archive) |
| Per-run working dirs | `runs/` (gitignored, tool-owned) |
| Browser session profile | `profile/` (gitignored, no credentials) |
| qq Tasks / backlog | `backlog/` (symlinked store, Backlog CLI) |

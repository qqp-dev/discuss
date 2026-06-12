# intent

## foundations

discuss is a single-operator local tool: one trigger drives the operator's already-logged-in UOPX student-portal session to the discussion with the soonest upcoming due date and runs one of two focused workflows — draft and fill the main post, or draft the two required classmate replies.

The tool assists the operator's own work and never ghostwrites-and-submits: it draws out the operator's stance and evidence, the editor step is mandatory, and the operator alone reviews and posts.

No run path ever locates or clicks a submit control: main-post mode fills the reply field and stops; peer-reply mode saves two drafts for manual paste.

The tool never stores, types, or automates credentials: the operator logs in by hand once, and a persistent browser profile carries that session across runs.

The tool is a respectful guest on a portal it does not own: human pace, the minimum pages the fixed click-path requires, no retry storms; at most one bounded, human-paced retry on a transient page-load timeout.

On any failure the tool stops and reports the specific failing step, preserving the operator's drafts on disk; it never proceeds on a guess.

A browser action is verified by reading the resulting state back — the reply field's rendered content equals the intended text — never by trusting that the call returned.

## structure

Every portal-specific selector and the entire click-path live in one adapter module; a portal markup change is a one-file fix, and the reply-field type is detected at runtime, never hard-coded.

Pure logic is fully covered against saved real portal HTML; the live-portal surface is coverage-exempt and verified by an operator-run live checklist — CI never touches the login-gated portal.

## work

discuss is linked to hypercore as an external project: intent.md is its single source of truth, and work/ holds the open asks — growing as they arrive, shrinking as they settle.

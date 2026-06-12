# intent

## foundations

discuss is a single-operator local tool: one trigger drives the operator's already-logged-in UOPX student-portal session to the discussion with the soonest upcoming due date and runs one of two focused workflows — draft and fill the main post, or draft the two required classmate replies.

The tool assists the operator's own work and never ghostwrites-and-submits: it draws out the operator's stance and evidence, the editor step is mandatory, and the operator alone reviews and posts.

No run path ever locates or clicks a submit control: main-post mode fills the reply field and stops; peer-reply mode saves two drafts for manual paste.

The tool never stores, types, or automates credentials: the operator logs in by hand once, and a persistent browser profile carries that session across runs. [machine]

The tool is a respectful guest on a portal it does not own: human pace, the minimum pages the fixed click-path requires, no retry storms; at most one bounded, human-paced retry on a transient page-load timeout. [machine]

On any failure the tool stops and reports the specific failing step, preserving the operator's drafts on disk; it never proceeds on a guess. [machine]

A browser action is verified by reading the resulting state back — the reply field's rendered content equals the intended text — never by trusting that the call returned. [machine]

## structure

contract.md is the single current truth for what discuss does and why; the implementation under src/ is its regenerable projection, and the archive — git history, CHANGELOG.md, the retired change packages — records how it got here. [machine]

discuss is a conforming instance of portable-core's Contract Loop, adopted by copy: change packages stay separate under changes/ until archive, each declares its contract impact, the collapse at archive updates exactly the declared sections, and a change is not done while the contract is stale with respect to it. [machine]

Every portal-specific selector and the entire click-path live in one adapter module; a portal markup change is a one-file fix, and the reply-field type is detected at runtime, never hard-coded. [machine]

Pure logic is fully covered against saved real portal HTML; the live-portal surface is coverage-exempt and verified by an operator-run live checklist — CI never touches the login-gated portal. [machine]

## work

discuss is linked to hypercore as an external project (registry entry, 2026-06-11): this file is its intent in hypercore's sense — its current intended reality, distilled from constitution.md, contract.md, and README.md, which remain its operating documents. Statements here are machine-drafted and unendorsed until ratified from hyper; work/ grows as asks arrive. [machine]

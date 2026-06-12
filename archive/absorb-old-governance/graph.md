# graph: absorb-old-governance

## absorb-old-governance

- ask: from the operator's supplant word and their approve of the link statement (hypercore 10ca01c, 843d9c6): intent.md is discuss's single source of truth — absorb what constitution.md and contract.md still carry (machine-read policy: coverage thresholds and exemptions, learning discipline; the Contract Loop's gates, schemas, lint, and change packages; README's overlapping claims) into intent, or retire it with them
- check: constitution.md and contract.md are gone from the repo, nothing left in it reads them, and every claim worth keeping stands in intent.md as a ratified statement
- result: absorbed and retired (d29cc51 and the four commits after it): constitution.md, contract.md, the vendored Contract Loop schemas and templates (method/), the change packages (changes/), and the conformance gate test are gone — git history keeps them; source docstrings and the README now cite intent.md instead of the retired documents; every claim worth keeping already stood ratified in intent.md, so nothing new entered [machine]; 96 tests pass
- state: folded
- since: 2026-06-11
- of: discuss

## no-claim-left-behind

- op: decide
- ask: does anything constitution.md/contract.md still carry need a new [machine] statement in intent.md?
- result: no — the nine ratified statements were distilled from exactly these documents (1d61c19, ratified through 71c402f) and the operator cut the two Contract Loop statements (2281d7b, 703345e); the coverage thresholds (85/75) and learning-discipline yaml were read only by the cut portable-core machinery and retire with it, the numeric thresholds superseded by the stricter ratified words "pure logic is fully covered"; behavior details (confirmation gate, config knobs, pipeline order) live in code and the README, not in governance
- state: done
- of: absorb-old-governance

## verify-nothing-reads-them

- op: check
- ask: after retirement, nothing in the repo reads constitution.md or contract.md, and the suite passes
- result: grep across src, tests, docs, templates, launcher, pyproject.toml and the README finds no reference; the only remaining mentions are CHANGELOG.md history entries, which record rather than read; 96 tests pass (the conformance gate's tests retired with it, including its two environment-skipped lint checks)
- state: done
- of: absorb-old-governance

# GAUSS Documentation QA System

## What This Is

A multi-tier quality assurance tool (`gauss-doc-qa`) for the GAUSS 26 Sphinx documentation (~1,700 RST files). Provides structural checks, cross-reference validation via the Sphinx dummy builder with custom GAUSS domain awareness, auto-fix for broken links with RST safety constraints, and AI persona-based reviews using Claude API structured outputs.

## Core Value

Every function in the Command Reference must have an accurate signature, correct examples, and be reachable from navigation — if the reference docs are wrong, users can't write GAUSS code.

## Requirements

### Validated

- ✓ docutils-based RST parser with doc type classification — v1.0
- ✓ Structural checkers (code blocks, sections, signatures) — v1.0
- ✓ Finding model with severity, path, line, category, message — v1.0
- ✓ CLI with scan, check-refs, fix, review subcommands — v1.0
- ✓ Terminal/JSON/Markdown report formatters — v1.0
- ✓ Sphinx dummy builder cross-reference validation — v1.0
- ✓ Broken link detection (:func:, :doc:, :ref:) with GAUSS domain — v1.0
- ✓ Orphan page detection with toctree walk — v1.0
- ✓ Function coverage analysis across code examples — v1.0
- ✓ See Also link validation — v1.0
- ✓ Auto-fix with fuzzy matching, leaf-text-only safety, dry-run default — v1.0
- ✓ Sphinx build verification after auto-fix — v1.0
- ✓ AI persona reviews with binary rubrics (Newcomer, Expert, Writer) — v1.0
- ✓ AI findings integrated into standard report pipeline — v1.0

### Active

- [ ] Terminology consistency enforcement via canonical glossary
- [ ] Top-N function deep validation (frequency-ranked)
- [ ] Cross-reference frequency ranking for function importance
- [ ] Diff-mode: only check files changed since last run
- [ ] :doc: and :ref: auto-fix (currently only :func:)

### Out of Scope

- Feedback widget / thumbs-up-down — requires deployment infrastructure
- Screenshot inventory — separate effort
- Mobile/PDF output validation — focus is on RST source quality
- CI integration — reports-only for now

## Context

- Docs live at `~/svn/gxmldoc/docs/` — Sphinx RST format
- Shipped v1.0 with 2,307 LOC source + 2,455 LOC tests (Python)
- Tech stack: Python, docutils, Sphinx (dummy builder), Click CLI, Rich terminal output, Anthropic SDK
- Custom GAUSS Sphinx domain uses `primary_domain='gauss'` and `default_role='any'` with case-insensitive matching
- 160+ tests across structural checks, cross-ref validation, auto-fix, and AI review

## Constraints

- **Source format**: RST/Sphinx — all checks must parse RST correctly
- **Doc location**: `~/svn/gxmldoc/docs/` — SVN working copy, not git
- **Language**: Python for all automation
- **Output**: Reports with findings + auto-fixes applied where safe

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python for scripts | RST parsing (docutils), cross-reference handling | ✓ Good |
| docutils AST not regex | RST whitespace sensitivity, directive nesting | ✓ Good |
| Sphinx dummy builder for xrefs | Full domain resolution without HTML output | ✓ Good |
| Batch AI with binary rubrics | Prevents hallucinated confidence, structured output | ✓ Good |
| Lazy imports for optional deps | Sphinx/anthropic don't break non-dependent commands | ✓ Good |
| Leaf-text-only auto-fix | RST corruption prevention for tables/directives/code | ✓ Good |
| Fuzzy match with 0.85 threshold | Balances recall vs false positive auto-fixes | — Pending validation on real corpus |

---
*Last updated: 2026-03-15 after v1.0 milestone*

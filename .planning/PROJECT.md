# GAUSS Documentation QA System

## What This Is

A comprehensive documentation QA tool (`gauss-doc-qa`) for the GAUSS 26 Sphinx documentation (~1,700 RST files). Provides structural checks, cross-reference validation, terminology enforcement, auto-fix for all reference types and glossary terms, AI persona reviews, frequency-based function ranking, deep validation, diff-mode incremental scanning, and glossary auto-generation.

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
- ✓ Canonical glossary file (YAML) with terminology scanner — v1.1
- ✓ Cross-reference frequency ranking with blog scraping — v1.1
- ✓ Top-100 function deep validation (structural + AI-assisted) — v1.1
- ✓ Deep validation per-function drill-down report — v1.1
- ✓ Extended auto-fix for :doc: and :ref: references — v1.2
- ✓ Glossary auto-fix for non-canonical terms — v1.2
- ✓ Diff-mode incremental scanning (date + SVN revision) — v1.2
- ✓ Glossary auto-generation from corpus term frequency — v1.2

### Active

(No active requirements — all shipped through v1.2)

### Out of Scope

- Feedback widget / thumbs-up-down — requires deployment infrastructure
- Screenshot inventory — separate effort
- Mobile/PDF output validation — focus is on RST source quality
- CI integration — reports-only for now

## Context

- Docs live at `~/svn/gxmldoc/docs/` — Sphinx RST format
- Shipped v1.2 with ~4,500 LOC source + ~5,200 LOC tests (Python)
- Tech stack: Python, docutils, Sphinx (dummy builder), Click CLI, Rich terminal output, Anthropic SDK
- Custom GAUSS Sphinx domain uses `primary_domain='gauss'` and `default_role='any'` with case-insensitive matching
- 300+ tests across all modules
- CLI: scan, check-refs, fix, review, freq, deep-validate, glossary-gen

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
| Doc xrefs + blog scraping for frequency | Combines internal docs signal with real-world usage | ✓ Good |
| N=100 for deep validation | Covers most-used functions without diminishing returns | ✓ Good |
| Deep validation separate from Finding model | Per-function pass/fail is different from per-line findings | ✓ Good |
| SVN mtime + svn diff for diff-mode | Works with SVN working copy without git | ✓ Good |
| Term extraction via docutils AST | Reuses existing parser, skips code blocks naturally | ✓ Good |

---
*Last updated: 2026-03-15 after v1.2 milestone*

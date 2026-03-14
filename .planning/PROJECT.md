# GAUSS Documentation QA System

## What This Is

A multi-tier quality assurance system for the GAUSS 26 Sphinx documentation (~1,700 RST files). Automated scripts catch structural issues (broken links, missing code blocks, orphaned pages), batch AI persona reviews validate docs by audience type, and targeted deep-validation of the most-referenced functions ensures the highest-traffic pages are correct.

## Core Value

Every function in the Command Reference must have an accurate signature, correct examples, and be reachable from navigation — if the reference docs are wrong, users can't write GAUSS code.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Automated link validation across all RST files
- [ ] Automated code block presence/non-empty checks
- [ ] Terminology consistency enforcement via canonical glossary
- [ ] Function coverage check (every Command Reference function appears in at least one code example)
- [ ] Orphan page detection (pages not linked from any toctree or cross-reference)
- [ ] Auto-fix capabilities for fixable issues (broken internal links, terminology deviations)
- [ ] AI persona batch reviews by doc type (4 personas, 4 doc sections)
- [ ] Top-N function deep validation (derived from cross-reference frequency in docs)
- [ ] Report generation with actionable findings per tier

### Out of Scope

- Feedback widget / thumbs-up-down (Tier 4) — requires deployment infrastructure, defer to later milestone
- Screenshot inventory — separate effort, not scriptable in the same way
- Mobile/PDF output validation — focus is on RST source quality
- CI integration — reports-only for now, CI hooks can come later

## Context

- Docs live at `~/svn/gxmldoc/docs/` — Sphinx RST format
- Doc sections: Command Reference (~1,400 individual function pages), Getting Started, User Guide, Graphics Guide
- Command Reference pages are one RST file per function (e.g., `abs.rst`, `acf.rst`)
- Getting Started and User Guide have subdirectories with topic pages
- Scripts will be Python, producing reports and auto-fixing where possible
- AI persona reviews will run as batch scripts (automated prompts against doc sections)
- Top-20 function list will be derived from cross-reference frequency analysis within the docs themselves

## Constraints

- **Source format**: RST/Sphinx — all checks must parse RST correctly
- **Doc location**: `~/svn/gxmldoc/docs/` — SVN working copy, not git
- **Language**: Python for all automation scripts
- **Output**: Reports with findings + auto-fixes applied where safe

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Python for scripts | RST parsing (docutils), cross-reference handling, glossary management | — Pending |
| Batch AI reviews | Consistent, repeatable, no manual intervention per page | — Pending |
| Derive top-20 from docs | No external analytics data needed; cross-ref frequency is a good proxy for importance | — Pending |
| Reports + auto-fix | Maximize leverage — fix what's fixable, report what needs judgment | — Pending |

---
*Last updated: 2026-03-14 after initialization*

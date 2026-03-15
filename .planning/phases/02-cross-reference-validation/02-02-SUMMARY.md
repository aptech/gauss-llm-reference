---
phase: 02-cross-reference-validation
plan: 02
subsystem: testing
tags: [sphinx, cross-references, orphan-detection, coverage, seealso, casefold]

requires:
  - phase: 01-foundation
    provides: BaseChecker pattern, models (Finding, ParsedDoc, Severity)
provides:
  - LinksChecker for broken :func:, :doc:, :ref: references (STRC-03)
  - OrphansChecker for unreachable toctree pages (STRC-04)
  - CoverageChecker for functions missing code examples (STRC-07)
  - SeeAlsoChecker for broken refs in seealso directives (STRC-08)
affects: [02-cross-reference-validation, 03-semantic-validation]

tech-stack:
  added: []
  patterns: [corpus-level checker with _computed caching, regex-based RST role extraction]

key-files:
  created:
    - gauss-doc-qa/src/gauss_doc_qa/checkers/links.py
    - gauss-doc-qa/src/gauss_doc_qa/checkers/orphans.py
    - gauss-doc-qa/src/gauss_doc_qa/checkers/coverage.py
    - gauss-doc-qa/src/gauss_doc_qa/checkers/seealso.py
    - gauss-doc-qa/tests/test_links.py
    - gauss-doc-qa/tests/test_orphans.py
    - gauss-doc-qa/tests/test_coverage.py
    - gauss-doc-qa/tests/test_seealso.py
  modified: []

key-decisions:
  - "Corpus-level checkers (orphans, coverage) use _computed flag and _findings cache to compute once across per-file calls"
  - "Read raw RST from parsed_doc.path for role extraction since docutils node lacks Sphinx cross-reference nodes"

patterns-established:
  - "Corpus-level checker pattern: _computed flag + _reset() for testing + per-file filtering on check()"
  - "ROLE_REF_RE regex for extracting Sphinx role references from raw RST"

requirements-completed: [STRC-03, STRC-04, STRC-07, STRC-08]

duration: 3min
completed: 2026-03-14
---

# Phase 02 Plan 02: Cross-Reference Validation Checkers Summary

**Four Sphinx-mode checkers for broken links, orphan pages, function coverage, and See Also validation using casefold() matching**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-15T02:56:46Z
- **Completed:** 2026-03-15T02:59:23Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- LinksChecker validates :func:, :doc:, :ref: references against Sphinx environment registries with case-insensitive matching
- OrphansChecker detects pages unreachable from root toctree, excluding :orphan: metadata pages and include fragments
- CoverageChecker flags Command Reference functions with no code example across the entire doc corpus
- SeeAlsoChecker validates cross-reference targets specifically within seealso directives
- 30 unit tests covering all checkers with mocked Sphinx environment data

## Task Commits

Each task was committed atomically:

1. **Task 1: Links and orphans checkers with tests** - `525d265` (feat)
2. **Task 2: Coverage and See Also checkers with tests** - `016c132` (feat)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/checkers/links.py` - Broken :func:, :doc:, :ref: reference detector
- `gauss-doc-qa/src/gauss_doc_qa/checkers/orphans.py` - Orphan page detector with toctree walking
- `gauss-doc-qa/src/gauss_doc_qa/checkers/coverage.py` - Function coverage checker across code blocks
- `gauss-doc-qa/src/gauss_doc_qa/checkers/seealso.py` - See Also directive cross-reference validator
- `gauss-doc-qa/tests/test_links.py` - 10 tests for links checker
- `gauss-doc-qa/tests/test_orphans.py` - 7 tests for orphans checker
- `gauss-doc-qa/tests/test_coverage.py` - 6 tests for coverage checker
- `gauss-doc-qa/tests/test_seealso.py` - 7 tests for seealso checker

## Decisions Made
- Corpus-level checkers (orphans, coverage) use `_computed` flag with `_findings` cache to compute once across per-file calls, with `_reset()` method for test isolation
- Read raw RST from `parsed_doc.path` for role extraction since docutils node lacks Sphinx cross-reference nodes

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All four Sphinx-mode checkers registered and following BaseChecker pattern
- Ready for CLI integration to pass sphinx_env and all_code_blocks kwargs
- Pre-existing test_sphinx_env.py import failure (missing sphinx package) is not caused by this plan

---
*Phase: 02-cross-reference-validation*
*Completed: 2026-03-14*

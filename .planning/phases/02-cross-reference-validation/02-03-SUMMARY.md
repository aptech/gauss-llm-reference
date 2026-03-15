---
phase: 02-cross-reference-validation
plan: 03
subsystem: cli
tags: [click, sphinx, cli, cross-reference]

requires:
  - phase: 02-cross-reference-validation
    provides: "Sphinx env loader (02-01) and four sphinx checkers (02-02)"
  - phase: 01-foundation
    provides: "CLI scan/inventory commands, checker registry, parser pipeline"
provides:
  - "check-refs CLI subcommand for cross-reference validation"
  - "--sphinx flag on scan command for combined fast+sphinx checks"
  - "All four sphinx checkers registered and discoverable"
  - "Shared _render_findings() helper for report output"
affects: [03-deep-validation, 04-ai-reviews]

tech-stack:
  added: []
  patterns: [lazy-import-for-optional-deps, shared-render-helper]

key-files:
  created: []
  modified:
    - gauss-doc-qa/src/gauss_doc_qa/cli.py
    - gauss-doc-qa/src/gauss_doc_qa/checkers/__init__.py
    - gauss-doc-qa/tests/test_cli.py

key-decisions:
  - "Lazy import for load_sphinx_env to keep CLI usable without sphinx installed"
  - "Factored _render_findings() helper to share rendering between scan and check-refs"
  - "Mock-based tests for check-refs to avoid requiring full Sphinx docs directory"

patterns-established:
  - "Lazy imports: Optional heavy dependencies imported inside functions that use them"
  - "Shared helpers: Common CLI output logic factored into module-level functions"

requirements-completed: [FOUN-02, STRC-03, STRC-04, STRC-07, STRC-08]

duration: 3min
completed: 2026-03-15
---

# Phase 2 Plan 3: CLI Integration Summary

**check-refs subcommand and --sphinx flag wiring all sphinx checkers into the CLI pipeline with shared rendering**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-15T03:01:48Z
- **Completed:** 2026-03-15T03:05:18Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added check-refs subcommand that loads Sphinx env and runs cross-reference validation checkers
- Added --sphinx flag on scan command for combined fast+sphinx checker execution
- Registered all four sphinx checkers (links, orphans, coverage, seealso) in checker package
- Factored out _render_findings() to eliminate rendering duplication between commands

## Task Commits

Each task was committed atomically:

1. **Task 1: Update checker registration and add check-refs CLI subcommand** - `6c98329` (feat)
2. **Task 1 fix: Lazy import for sphinx_env** - `7d1ba63` (fix)
3. **Task 2: CLI integration tests** - `1c74c36` (test)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/checkers/__init__.py` - Registers all four sphinx checkers, exports get_all_sphinx_checkers
- `gauss-doc-qa/src/gauss_doc_qa/cli.py` - check-refs subcommand, --sphinx flag, _render_findings() helper
- `gauss-doc-qa/tests/test_cli.py` - 7 new integration tests for check-refs, --sphinx, and checker registration

## Decisions Made
- Used lazy import for `load_sphinx_env` inside functions to prevent import errors when sphinx is not installed -- keeps CLI functional for fast-only operations
- Factored `_render_findings()` helper from scan command's inline rendering to share between scan and check-refs
- Used mock-based testing with `patch("gauss_doc_qa.parser.sphinx_env.load_sphinx_env")` to test CLI wiring without requiring full Sphinx build

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fixed module-level import causing ModuleNotFoundError**
- **Found during:** Task 2 (CLI integration tests)
- **Issue:** `from gauss_doc_qa.parser.sphinx_env import load_sphinx_env` at module level caused ImportError when sphinx not installed, breaking all CLI tests
- **Fix:** Moved import inside `scan()` and `check_refs()` functions (lazy import pattern)
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/cli.py
- **Verification:** All 122 tests pass including new CLI tests
- **Committed in:** 7d1ba63

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential fix for test environment compatibility. No scope creep.

## Issues Encountered
None beyond the lazy import fix documented above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 (Cross-Reference Validation) is now complete
- All sphinx-mode checkers are wired into the CLI and accessible via check-refs and scan --sphinx
- Full test suite passes (122 tests)
- Ready for Phase 3 (Deep Validation) or Phase 4 (AI Reviews)

---
*Phase: 02-cross-reference-validation*
*Completed: 2026-03-15*

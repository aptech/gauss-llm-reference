---
phase: 03-auto-fix
plan: 02
subsystem: cli
tags: [click, rich, cli, auto-fix, dry-run]

requires:
  - phase: 03-01
    provides: "Fixer module with resolver, applier, and verify components"
provides:
  - "gauss-qa fix subcommand with dry-run/apply/verify modes"
  - "CLI integration tests for fix subcommand"
affects: [04-ai-reviews]

tech-stack:
  added: []
  patterns: [lazy-import for sphinx, sys.modules stub for testing without sphinx]

key-files:
  created:
    - gauss-doc-qa/tests/test_fix_cli.py
  modified:
    - gauss-doc-qa/src/gauss_doc_qa/fixer/__init__.py
    - gauss-doc-qa/src/gauss_doc_qa/cli.py

key-decisions:
  - "Used sys.modules stub pattern to enable patching sphinx_env without sphinx installed"
  - "Used truly broken refs (plotBr not plotbar) in tests since LinksChecker is case-insensitive"

patterns-established:
  - "sys.modules stub fixture: inject MagicMock into sys.modules for modules requiring unavailable deps"

requirements-completed: [FIXR-02, FIXR-04]

duration: 4min
completed: 2026-03-15
---

# Phase 3 Plan 2: Fix CLI Subcommand Summary

**gauss-qa fix command with dry-run default, --apply write mode, --verify Sphinx build check, and Rich diff output**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-15T03:38:41Z
- **Completed:** 2026-03-15T03:42:43Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Wired fixer module into CLI as `gauss-qa fix` subcommand with --apply, --verify, --min-confidence options
- Default dry-run mode shows Rich-formatted diff preview with confidence scores
- Created 6 integration tests covering all CLI modes (dry-run, apply, verify, min-confidence filter)

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix CLI subcommand with dry-run/apply/verify and Rich diff output** - `c470d14` (feat)
2. **Task 2: CLI integration tests for fix subcommand** - `cb3786a` (test)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/fixer/__init__.py` - Public API exports for fixer module
- `gauss-doc-qa/src/gauss_doc_qa/cli.py` - fix subcommand with dry-run/apply/verify modes
- `gauss-doc-qa/tests/test_fix_cli.py` - 6 integration tests for fix subcommand

## Decisions Made
- Used sys.modules stub pattern to inject mock sphinx_env module for testing without sphinx installed, since existing test_cli.py sphinx tests fail without sphinx
- Used "plotBr" as broken ref target in tests instead of "plotbar" because LinksChecker does case-insensitive matching (plotbar casefolds to match plotBar), so only truly misspelled refs generate findings

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Sphinx not installed in test environment causes test_cli.py sphinx tests to fail; this is pre-existing and not caused by this plan. Worked around in test_fix_cli.py with sys.modules stub fixture.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Fix CLI complete with full test coverage
- Phase 3 (Auto-Fix Engine) complete - both resolver module and CLI integration done
- Ready for Phase 4 (AI Reviews)

---
*Phase: 03-auto-fix*
*Completed: 2026-03-15*

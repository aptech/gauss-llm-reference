---
phase: 03-auto-fix
plan: 01
subsystem: fixer
tags: [difflib, fuzzy-matching, rst, sphinx, cross-references]

requires:
  - phase: 02-cross-ref
    provides: Finding model with broken_func_ref/broken_seealso_ref categories, Sphinx env loader
provides:
  - FixProposal dataclass for proposed cross-reference corrections
  - resolve_func_ref() fuzzy matcher with ambiguity detection
  - resolve_fixes() Finding-to-FixProposal converter
  - is_safe_to_fix() leaf-text-only safety gate
  - apply_fixes() bottom-up RST file editor with dry-run support
  - verify_sphinx_build() warning capture for post-fix validation
affects: [03-auto-fix]

tech-stack:
  added: [difflib]
  patterns: [fuzzy-match-with-ambiguity-gate, leaf-text-only-safety, bottom-up-line-editing]

key-files:
  created:
    - gauss-doc-qa/src/gauss_doc_qa/fixer/__init__.py
    - gauss-doc-qa/src/gauss_doc_qa/fixer/models.py
    - gauss-doc-qa/src/gauss_doc_qa/fixer/resolver.py
    - gauss-doc-qa/src/gauss_doc_qa/fixer/applier.py
    - gauss-doc-qa/src/gauss_doc_qa/fixer/verify.py
    - gauss-doc-qa/tests/test_resolver.py
    - gauss-doc-qa/tests/test_applier.py
    - gauss-doc-qa/tests/test_verify.py
    - gauss-doc-qa/tests/fixtures/broken_refs.rst
  modified: []

key-decisions:
  - "Used difflib.get_close_matches with casefolded names for case-insensitive fuzzy matching"
  - "Ambiguity threshold of 0.05 score gap between top two matches"
  - "Sphinx import behind try/except with _get_sphinx_cls() accessor for testability without sphinx installed"

patterns-established:
  - "Ambiguity gate: top-2 match score gap > 0.05 required for acceptance"
  - "Leaf-text-only: tables, code blocks, directives rejected; paragraphs and seealso accepted"
  - "Bottom-up line processing: proposals sorted descending by line number to preserve indices"

requirements-completed: [FIXR-01, FIXR-03, FIXR-04]

duration: 4min
completed: 2026-03-15
---

# Phase 3 Plan 1: Core Fixer Module Summary

**Fuzzy-match resolver for broken :func: refs with leaf-text-only safe RST editing and Sphinx build verification**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-15T03:32:02Z
- **Completed:** 2026-03-15T03:36:08Z
- **Tasks:** 2
- **Files created:** 9

## Accomplishments
- FixProposal model and fuzzy-match resolver using difflib with ambiguity detection
- Safe RST applier that rejects table, code block, and directive lines
- Sphinx build verifier that captures warning counts for post-fix validation
- 28 unit tests covering resolver, applier safety, and verification

## Task Commits

Each task was committed atomically:

1. **Task 1: FixProposal model, resolver with fuzzy matching, and test fixture** - `962a805` (feat)
2. **Task 2: Safe applier with leaf-text-only constraint and Sphinx verification** - `ee30317` (feat)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/fixer/__init__.py` - Package init
- `gauss-doc-qa/src/gauss_doc_qa/fixer/models.py` - FixProposal dataclass
- `gauss-doc-qa/src/gauss_doc_qa/fixer/resolver.py` - Fuzzy matching and Finding-to-FixProposal conversion
- `gauss-doc-qa/src/gauss_doc_qa/fixer/applier.py` - Safety checks and bottom-up file editing
- `gauss-doc-qa/src/gauss_doc_qa/fixer/verify.py` - Sphinx build warning capture
- `gauss-doc-qa/tests/test_resolver.py` - 10 resolver tests
- `gauss-doc-qa/tests/test_applier.py` - 14 applier tests
- `gauss-doc-qa/tests/test_verify.py` - 4 verify tests
- `gauss-doc-qa/tests/fixtures/broken_refs.rst` - Test fixture with broken refs

## Decisions Made
- Used difflib.get_close_matches with casefolded names for case-insensitive fuzzy matching
- Ambiguity threshold set at 0.05 score gap between top two matches (returns None if ambiguous)
- Sphinx import wrapped in try/except with _get_sphinx_cls() accessor so tests work without sphinx installed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed ambiguous test case**
- **Found during:** Task 1 (resolver tests)
- **Issue:** Test used "plot" as ambiguous target but it matched "plotXY" unambiguously (0.8 score)
- **Fix:** Changed test to use "plotBa" against ["plotBar", "plotBax", "plotBaz"] for true ambiguity
- **Files modified:** gauss-doc-qa/tests/test_resolver.py
- **Committed in:** 962a805

**2. [Rule 3 - Blocking] Restructured verify.py for testability without sphinx**
- **Found during:** Task 2 (verify tests)
- **Issue:** Sphinx not installed in test environment; lazy import inside function couldn't be patched
- **Fix:** Module-level try/except import with _get_sphinx_cls() accessor function that tests can patch
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/fixer/verify.py, gauss-doc-qa/tests/test_verify.py
- **Committed in:** ee30317

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both fixes necessary for test correctness and testability. No scope creep.

## Issues Encountered
- Pre-existing test failures in test_sphinx_env.py and test_cli.py due to sphinx not being installed -- out of scope, not caused by this plan's changes

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Fixer package complete with models, resolver, applier, and verifier
- Ready for CLI integration (fix command) and end-to-end testing

---
*Phase: 03-auto-fix*
*Completed: 2026-03-15*

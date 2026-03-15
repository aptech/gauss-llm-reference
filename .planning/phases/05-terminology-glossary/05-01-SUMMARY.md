---
phase: 05-terminology-glossary
plan: 01
subsystem: testing
tags: [glossary, yaml, terminology, regex, checker]

# Dependency graph
requires:
  - phase: 01-foundation
    provides: BaseChecker, Finding, ParsedDoc models and checker registry
provides:
  - GlossaryEntry dataclass and YAML loader with validation
  - build_alias_map for O(1) case-insensitive alias lookup
  - GlossaryChecker extending BaseChecker with line-by-line RST scanning
  - Code block and literal block skipping to prevent false positives
  - 19 unit tests covering model, loader, alias map, and checker
affects: [05-02, cli-integration]

# Tech tracking
tech-stack:
  added: [pyyaml]
  patterns: [non-auto-registered checker pattern for config-dependent checkers]

key-files:
  created:
    - gauss-doc-qa/src/gauss_doc_qa/glossary.py
    - gauss-doc-qa/src/gauss_doc_qa/checkers/glossary.py
    - gauss-doc-qa/tests/test_glossary.py
  modified:
    - gauss-doc-qa/pyproject.toml

key-decisions:
  - "GlossaryChecker not auto-registered -- requires runtime glossary data, instantiated by CLI when --glossary provided"
  - "Combined regex alternation pattern for all aliases, sorted by length descending for correct multi-word matching"
  - "build_alias_map allows same-entry case-variant aliases (Gauss/gauss both map to GAUSS entry)"

patterns-established:
  - "Non-auto-registered checker: checkers needing config are not imported in __init__.py, instantiated at CLI level"
  - "Code block skipping heuristic: track directive + indentation state for RST code block detection"

requirements-completed: [GLOS-01, GLOS-02]

# Metrics
duration: 3min
completed: 2026-03-15
---

# Phase 5 Plan 1: Glossary Model and Checker Summary

**YAML glossary loader with validation, GlossaryChecker scanning RST for non-canonical terms with code block skipping and word-boundary matching**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-15T11:01:15Z
- **Completed:** 2026-03-15T11:04:11Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- GlossaryEntry dataclass with YAML loader that validates canonical terms, aliases, categories
- GlossaryChecker that scans RST line-by-line with pre-compiled combined regex for all aliases
- Code block and literal block content excluded from scanning (no false positives)
- 19 unit tests covering loading, validation errors, alias map conflicts, checker behavior, word boundaries

## Task Commits

Each task was committed atomically:

1. **Task 1: Glossary model and YAML loader** - `e5b0984` (feat)
2. **Task 2: GlossaryChecker and registration** - `585b8e7` (feat)
3. **Task 3: Unit tests for glossary model and checker** - `69fb36d` (test)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/glossary.py` - GlossaryEntry dataclass, load_glossary(), build_alias_map()
- `gauss-doc-qa/src/gauss_doc_qa/checkers/glossary.py` - GlossaryChecker extending BaseChecker with line-by-line RST scanning
- `gauss-doc-qa/tests/test_glossary.py` - 19 tests for model, loader, alias map, and checker
- `gauss-doc-qa/pyproject.toml` - Added pyyaml>=6.0 dependency

## Decisions Made
- GlossaryChecker not auto-registered at import time -- requires runtime glossary data, CLI instantiates when --glossary provided
- Combined regex alternation sorted by length descending ensures multi-word aliases like "data frame" match before shorter substrings
- build_alias_map allows same-entry case-variant aliases (e.g., "Gauss" and "gauss" both lowercase to "gauss") without conflict

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added pyyaml to pyproject.toml dependencies**
- **Found during:** Task 1
- **Issue:** pyyaml not listed in project dependencies despite being required by glossary loader
- **Fix:** Added "pyyaml>=6.0" to dependencies in pyproject.toml and installed in venv
- **Files modified:** gauss-doc-qa/pyproject.toml
- **Verification:** import yaml succeeds in project venv
- **Committed in:** e5b0984 (Task 1 commit)

**2. [Rule 1 - Bug] Fixed build_alias_map same-entry case-variant conflict**
- **Found during:** Task 3
- **Issue:** Aliases "Gauss" and "gauss" within same entry both lowercased to "gauss", triggering false conflict error
- **Fix:** Added identity check (existing is not entry) before raising ValueError
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/glossary.py
- **Verification:** All 19 tests pass
- **Committed in:** 69fb36d (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 bug)
**Impact on plan:** Both fixes necessary for correctness. No scope creep.

## Issues Encountered
None beyond the auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Glossary model and checker are complete and tested
- Ready for 05-02: CLI --glossary integration and end-to-end report tests
- GlossaryChecker designed for easy CLI instantiation with glossary file path

---
*Phase: 05-terminology-glossary*
*Completed: 2026-03-15*

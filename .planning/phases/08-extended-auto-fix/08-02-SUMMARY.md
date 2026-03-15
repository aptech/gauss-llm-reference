---
phase: 08-extended-auto-fix
plan: 02
subsystem: cli
tags: [click, glossary, auto-fix, cross-references]

requires:
  - phase: 08-extended-auto-fix-01
    provides: "resolve_fixes with doc/ref routing, resolve_glossary_fixes, apply_fixes"
provides:
  - "CLI fix command with --glossary flag for terminology auto-fix"
  - "CLI fix command passing doc_names/label_names for :doc:/:ref: resolution"
  - "Integration tests covering all extended fix modes"
affects: [09-diff-mode, 10-glossary-generation]

tech-stack:
  added: []
  patterns: ["CLI option wiring with lazy imports for optional features"]

key-files:
  created:
    - gauss-doc-qa/tests/test_fix_cli.py (7 new test cases)
  modified:
    - gauss-doc-qa/src/gauss_doc_qa/cli.py

key-decisions:
  - "Glossary fixes combined with ref fixes into single proposals list before apply"
  - "doc_names/label_names extracted from env inline rather than passed as CLI args"

patterns-established:
  - "Glossary option uses click.Path(exists=True) for validation before load"

requirements-completed: [EFIX-01, EFIX-02, EFIX-03, GFIX-01, GFIX-02, GFIX-03]

duration: 3min
completed: 2026-03-15
---

# Phase 8 Plan 2: Extended Fix CLI Summary

**CLI fix command wired for :doc:/:ref: resolution and --glossary terminology auto-fix with dry-run default**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-15T12:38:52Z
- **Completed:** 2026-03-15T12:42:16Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Extended fix subcommand to pass doc_names and label_names enabling :doc: and :ref: fuzzy resolution
- Added --glossary option that loads YAML glossary, runs GlossaryChecker, and combines terminology proposals with ref proposals
- 7 new integration tests covering doc ref, ref, glossary dry-run/apply, code block safety, and combined mode

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend fix CLI to handle :doc:, :ref:, and glossary fixes** - `0bd3fd7` (feat)
2. **Task 2: CLI integration tests for extended fix modes** - `c38a39a` (test)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/cli.py` - Extended fix command with --glossary flag, doc_names/label_names pass-through
- `gauss-doc-qa/tests/test_fix_cli.py` - 7 new integration tests for extended fix modes

## Decisions Made
- Glossary fixes are combined into the same proposals list as ref fixes, so apply_fixes handles them uniformly
- doc_names and label_names are extracted from env.all_docs and env.domaindata["std"]["labels"] inline in the fix command

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 8 complete: all extended auto-fix features (resolvers + CLI) are implemented and tested
- Ready for Phase 9 (diff-mode) or Phase 10 (glossary generation)

---
*Phase: 08-extended-auto-fix*
*Completed: 2026-03-15*

---
phase: 10-glossary-generation
plan: 01
subsystem: tooling
tags: [glossary, yaml, docutils, nlp, term-extraction, cli]

requires:
  - phase: 05-glossary-checking
    provides: GlossaryEntry model, load_glossary YAML loader
  - phase: 01-foundation
    provides: RST parser, ParsedDoc model, CLI framework
provides:
  - glossary_gen.py module with extract_terms, group_terms, generate_glossary_yaml
  - glossary-gen CLI subcommand with --min-freq and -o options
affects: []

tech-stack:
  added: []
  patterns:
    - "docutils AST traversal for text extraction (paragraph, title, term nodes)"
    - "regex-based multi-word and proper noun term extraction"
    - "case-insensitive grouping with plural/singular merging"

key-files:
  created:
    - gauss-doc-qa/src/gauss_doc_qa/glossary_gen.py
    - gauss-doc-qa/tests/test_glossary_gen.py
  modified:
    - gauss-doc-qa/src/gauss_doc_qa/cli.py

key-decisions:
  - "Added all-caps regex pattern alongside proper noun pattern to capture terms like GAUSS, ARIMA"
  - "Separate 2-word regex to ensure 2-word terms captured even when 3-word supersets exist"
  - "Lazy import of glossary_gen in CLI to avoid overhead when subcommand not used"

patterns-established:
  - "Term extraction via docutils AST node traversal with ancestor-based exclusion"

requirements-completed: [GGEN-01, GGEN-02, GGEN-03]

duration: 3min
completed: 2026-03-15
---

# Phase 10 Plan 01: Glossary Generation Summary

**Auto-generate draft glossary YAML from corpus term frequency with docutils AST extraction, case/plural grouping, and CLI subcommand**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-15T13:00:46Z
- **Completed:** 2026-03-15T13:03:54Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Term extraction module that walks docutils AST, skipping code blocks and system messages
- Case variant and plural/singular grouping with configurable minimum frequency
- YAML output compatible with existing load_glossary() (round-trip verified)
- CLI glossary-gen subcommand with --min-freq and -o flags

## Task Commits

Each task was committed atomically:

1. **Task 1: Term extraction and grouping module with tests** (TDD)
   - `7548669` (test: failing tests for glossary generation)
   - `4035271` (feat: implement glossary generation module)
2. **Task 2: Wire glossary-gen subcommand into CLI** - `ec9600f` (feat)

## Files Created/Modified
- `gauss-doc-qa/src/gauss_doc_qa/glossary_gen.py` - extract_terms, group_terms, generate_glossary_yaml functions
- `gauss-doc-qa/tests/test_glossary_gen.py` - 11 tests covering extraction, grouping, and YAML output
- `gauss-doc-qa/src/gauss_doc_qa/cli.py` - Added glossary-gen subcommand

## Decisions Made
- Added all-caps regex pattern (r'\b([A-Z]{3,})\b') to capture terms like GAUSS, ARIMA alongside the proper noun pattern
- Added separate 2-word capitalized regex to ensure "Time Series" captured even when 3-word "Time Series analysis" also matches
- Glossary entries with only one variant still get an alias (lowercase/uppercase form) to satisfy load_glossary validation

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] All-caps terms not captured by proper noun regex**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** _PROPER_NOUN_RE `[A-Z][a-z]{3,}` requires lowercase letters after the capital, so "GAUSS" (all caps) was missed
- **Fix:** Added _ALL_CAPS_RE pattern `[A-Z]{3,}` to also capture all-uppercase terms
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/glossary_gen.py
- **Verification:** test_extract_terms_from_paragraphs now passes
- **Committed in:** 4035271

**2. [Rule 1 - Bug] 2-word terms subsumed by 3-word regex**
- **Found during:** Task 1 (GREEN phase)
- **Issue:** _MULTIWORD_RE captures "Time Series analysis" (3 words) but not "Time Series" (2 words) separately
- **Fix:** Added _MULTIWORD_2_RE pattern to independently capture 2-word capitalized terms
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/glossary_gen.py
- **Verification:** test_extract_terms_captures_multiword now passes
- **Committed in:** 4035271

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes necessary for correct term extraction. No scope creep.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Glossary generation complete, no further phases planned in v1.2 milestone
- All v1.2 features (diff-mode, auto-fix, glossary generation) are complete

## Self-Check: PASSED

All files and commits verified.

---
*Phase: 10-glossary-generation*
*Completed: 2026-03-15*

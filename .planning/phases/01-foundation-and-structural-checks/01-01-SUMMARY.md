---
phase: 01-foundation-and-structural-checks
plan: 01
subsystem: parser
tags: [docutils, rst, dataclasses, python, ast-parsing]

# Dependency graph
requires: []
provides:
  - "ParsedDoc, Finding, Severity, DocType, CodeBlock dataclasses in models.py"
  - "parse_rst() function producing ParsedDoc from RST content via docutils AST"
  - "classify_doc() function mapping file paths to DocType enum values"
  - "scan_docs_dir() inventory scanner with fnmatch exclusion patterns"
  - "8 RST test fixtures covering all doc types and failure modes"
affects: [01-02, 01-03, 02-cross-reference-checks]

# Tech tracking
tech-stack:
  added: [docutils 0.22.4, rich 14.3.3, click 8.3.1, pytest 9.0.2]
  patterns: [docutils-ast-traversal, path-based-classification, system-message-field-extraction]

key-files:
  created:
    - "gauss-doc-qa/pyproject.toml"
    - "gauss-doc-qa/src/gauss_doc_qa/models.py"
    - "gauss-doc-qa/src/gauss_doc_qa/parser/rst_parser.py"
    - "gauss-doc-qa/src/gauss_doc_qa/parser/classifier.py"
    - "gauss-doc-qa/src/gauss_doc_qa/parser/inventory.py"
    - "gauss-doc-qa/tests/fixtures/"
  modified: []

key-decisions:
  - "Used findall() instead of deprecated traverse() for docutils 0.22.4 compatibility"
  - "Extract fields from system_message literal_blocks to handle unrecognized Sphinx directives (.. function::)"
  - "Filter system_message literal_blocks from code_block extraction to avoid false positives"
  - "Corrected pyproject.toml build-backend from invalid setuptools.backends._legacy to setuptools.build_meta"
  - "Empty code block fixture uses placeholder '...' since docutils drops truly whitespace-only literal_blocks"

patterns-established:
  - "AST-only extraction: all structural data comes from docutils node traversal, never regex on RST source"
  - "System message fallback: Sphinx-only directives produce system_message nodes; field extraction handles both standard and fallback paths"
  - "Path-based classification: DocType determined by file path components before any content parsing"

requirements-completed: [FOUN-01, FOUN-03]

# Metrics
duration: 7min
completed: 2026-03-14
---

# Phase 1 Plan 1: Foundation Models and Parser Summary

**Docutils-based RST parser with doc type classification, field extraction from Sphinx directive fallbacks, and inventory scanner with conf.py exclusion patterns**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-14T21:41:16Z
- **Completed:** 2026-03-14T21:48:24Z
- **Tasks:** 2
- **Files modified:** 20

## Accomplishments
- Complete data model layer with Finding, Severity, DocType, CodeBlock, ParsedDoc dataclasses
- RST parser producing full ParsedDoc from docutils AST with section, code block, and field list extraction
- Doc type classifier with 6-rule priority chain covering all 9 DocType variants
- Inventory scanner with fnmatch-based exclusion patterns from Sphinx conf.py
- 44 passing unit tests across models, parser, and classifier

## Task Commits

Each task was committed atomically:

1. **Task 1: Project skeleton, models, and test fixtures** - `40564ae` (feat)
2. **Task 2: RST parser, doc type classifier, inventory scanner, and tests** - `15040b1` (feat)

## Files Created/Modified
- `gauss-doc-qa/pyproject.toml` - Project configuration with docutils, rich, click dependencies
- `gauss-doc-qa/src/gauss_doc_qa/models.py` - Finding, Severity, DocType, CodeBlock, ParsedDoc dataclasses
- `gauss-doc-qa/src/gauss_doc_qa/parser/rst_parser.py` - docutils-based RST parsing with system_message fallback
- `gauss-doc-qa/src/gauss_doc_qa/parser/classifier.py` - Path-based DocType classification
- `gauss-doc-qa/src/gauss_doc_qa/parser/inventory.py` - Directory scanner with exclusion patterns
- `gauss-doc-qa/tests/fixtures/` - 8 RST test fixtures for all doc types and failure modes
- `gauss-doc-qa/tests/test_models.py` - 21 model unit tests
- `gauss-doc-qa/tests/test_parser.py` - 10 parser tests
- `gauss-doc-qa/tests/test_classifier.py` - 13 classifier tests

## Decisions Made
- **findall() over traverse():** docutils 0.22.4 deprecates `traverse()` in favor of `findall()`. Using the modern API avoids deprecation warnings.
- **System message field extraction:** Standalone docutils cannot parse Sphinx-specific `.. function::` directives. These become `system_message` nodes with the directive content as a `literal_block` child. The parser extracts `:param:` and `:return:` fields from these via regex as a fallback path.
- **Filtering system_message literal_blocks from code blocks:** The literal_block inside a system_message contains directive source text, not actual code examples. These are excluded from `code_blocks` by checking ancestor node types.
- **Build backend correction:** The plan specified `setuptools.backends._legacy:_Backend` which does not exist. Changed to `setuptools.build_meta`.
- **Empty code block limitation:** docutils drops `::` blocks followed by whitespace-only content entirely (no literal_block node created). The empty_code fixture uses `...` placeholder content. The STRC-02 check will need raw source analysis for the truly-empty case.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed pyproject.toml build backend**
- **Found during:** Task 1 (project skeleton)
- **Issue:** Plan specified `setuptools.backends._legacy:_Backend` as build-backend, which does not exist in setuptools
- **Fix:** Changed to `setuptools.build_meta` (the standard setuptools PEP 517 backend)
- **Files modified:** gauss-doc-qa/pyproject.toml
- **Committed in:** 40564ae

**2. [Rule 1 - Bug] Fixed system_message field extraction for Sphinx directives**
- **Found during:** Task 2 (parser implementation)
- **Issue:** `.. function::` directives are not recognized by standalone docutils. Field lists (`:param:`, `:return:`) inside these directives are not parsed as `nodes.field_list` -- they appear as text inside a `literal_block` child of a `system_message` node.
- **Fix:** Added fallback extraction path that parses field entries from system_message literal_block text via regex
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/parser/rst_parser.py
- **Committed in:** 15040b1

**3. [Rule 1 - Bug] Excluded system_message literal_blocks from code block results**
- **Found during:** Task 2 (parser implementation)
- **Issue:** The `.. function::` directive content appeared as a spurious code block because its literal_block child was included in code_block extraction
- **Fix:** Added ancestor check to skip literal_blocks inside system_message nodes
- **Files modified:** gauss-doc-qa/src/gauss_doc_qa/parser/rst_parser.py
- **Committed in:** 15040b1

**4. [Rule 1 - Bug] Updated empty_code fixture for docutils behavior**
- **Found during:** Task 2 (parser testing)
- **Issue:** docutils drops `::` blocks with whitespace-only content entirely, producing no literal_block node
- **Fix:** Changed fixture to use `...` placeholder content; documented the limitation for future STRC-02 implementation
- **Files modified:** gauss-doc-qa/tests/fixtures/empty_code.rst, gauss-doc-qa/tests/test_parser.py
- **Committed in:** 15040b1

---

**Total deviations:** 4 auto-fixed (4 bugs)
**Impact on plan:** All fixes necessary for correctness. The system_message handling is essential for the parser to work with real GAUSS documentation. No scope creep.

## Issues Encountered
- Python 3.14 on macOS requires a virtual environment (PEP 668 externally managed). Created `.venv` in project directory.
- docutils 0.22.4 deprecation warnings for OptionParser and traverse() -- switched to findall() API.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All model dataclasses and parser infrastructure ready for checkers (Plan 02) and reporters (Plan 03)
- The `.. function::` directive handling pattern is established for signature checking
- Empty code block detection via AST has a known limitation; the STRC-02 checker may need to supplement with raw source analysis
- Inventory scanner is ready to process the full GAUSS docs corpus (~1,700 files)

## Self-Check: PASSED

All 19 created files verified present. Both task commits (40564ae, 15040b1) verified in git log. 44 tests passing.

---
*Phase: 01-foundation-and-structural-checks*
*Completed: 2026-03-14*

# Roadmap: GAUSS Documentation QA System

## Overview

Build a multi-tier quality assurance system for ~1,700 RST files in the GAUSS Sphinx documentation. Phase 1 establishes the parsing foundation, doc classifier, reporting pipeline, and fast structural checks (zero external dependencies, immediate value). Phase 2 loads the Sphinx environment with the custom GAUSS domain for cross-reference validation, orphan detection, and function coverage. Phase 3 adds conservative auto-fix for safely correctable issues. Phase 4 integrates Claude API persona reviews for qualitative validation across doc sections.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Foundation and Structural Checks** - Parse RST via docutils, classify doc types, run fast structural checks, output reports
- [x] **Phase 2: Cross-Reference Validation** - Load Sphinx environment with GAUSS domain for link resolution, orphan detection, and function coverage (completed 2026-03-15)
- [ ] **Phase 3: Auto-Fix** - Conservative automated corrections for broken links and structural issues with dry-run safety
- [ ] **Phase 4: AI Persona Reviews** - Batch Claude API reviews with structured rubrics across 3 personas and doc sections

## Phase Details

### Phase 1: Foundation and Structural Checks
**Goal**: User can scan the entire doc corpus for structural issues and get actionable reports
**Depends on**: Nothing (first phase)
**Requirements**: FOUN-01, FOUN-03, FOUN-04, STRC-01, STRC-02, STRC-05, STRC-06, REPT-01, REPT-02, REPT-03, REPT-04
**Success Criteria** (what must be TRUE):
  1. Running the CLI against the GAUSS docs directory produces a report listing Command Reference pages missing code blocks, missing required sections, or incomplete function signatures
  2. Every finding in the report includes file path, line number, severity level, and category
  3. Reports are available in terminal (with color), JSON, and Markdown formats
  4. Report header shows summary counts grouped by category and severity
  5. The tool correctly classifies RST files by doc type (function page, operator page, guide, index, fragment) and uses docutils AST parsing, not regex
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Project skeleton, models, RST parser, classifier, inventory scanner
- [x] 01-02-PLAN.md — Structural checkers (code blocks, sections, signatures) with registry
- [x] 01-03-PLAN.md — CLI entry point, report formatters (terminal/JSON/markdown), end-to-end wiring

### Phase 2: Cross-Reference Validation
**Goal**: User can detect broken links, orphan pages, and uncovered functions using full Sphinx-aware resolution
**Depends on**: Phase 1
**Requirements**: FOUN-02, STRC-03, STRC-04, STRC-07, STRC-08
**Success Criteria** (what must be TRUE):
  1. Running the cross-reference check identifies broken :func:, :doc:, and :ref: links that fail to resolve through the custom GAUSS domain
  2. Orphan page detection correctly identifies RST files not in any toctree while respecting :orphan: directives and include fragments
  3. Function coverage report lists Command Reference functions whose names never appear in any code example across the docs
  4. See Also links that point to non-existent function pages are flagged
**Plans**: 3 plans

Plans:
- [ ] 02-01-PLAN.md — Sphinx environment loader, dependency updates, get_all_sphinx_checkers() helper
- [ ] 02-02-PLAN.md — Four Sphinx-mode checkers (links, orphans, coverage, seealso) with unit tests
- [ ] 02-03-PLAN.md — CLI check-refs subcommand, --sphinx flag on scan, integration tests

### Phase 3: Auto-Fix
**Goal**: User can automatically correct safely-fixable issues without risking RST corruption
**Depends on**: Phase 2
**Requirements**: FIXR-01, FIXR-02, FIXR-03, FIXR-04
**Success Criteria** (what must be TRUE):
  1. Running auto-fix in dry-run mode (the default) shows proposed changes without modifying any files
  2. When applied, auto-fix corrects broken internal links where the target is unambiguously determinable
  3. Auto-fix only modifies leaf text nodes -- tables, directive structures, and code blocks are never touched
  4. After auto-fix is applied, a Sphinx build verification confirms no RST corruption was introduced
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Fixer module: models, resolver (fuzzy matching), applier (leaf-text safety), Sphinx verifier
- [ ] 03-02-PLAN.md — CLI fix subcommand with dry-run/apply/verify, integration tests

### Phase 4: AI Persona Reviews
**Goal**: User can run batch AI reviews that evaluate docs from distinct audience perspectives with structured, actionable findings
**Depends on**: Phase 1
**Requirements**: AIRV-01, AIRV-02, AIRV-03, AIRV-04, AIRV-05
**Success Criteria** (what must be TRUE):
  1. Running a persona review submits doc sections to Claude API with structured binary rubrics (pass/fail per criterion, not free-text)
  2. New GAUSS user persona reviews Getting Started content and identifies points of confusion
  3. Experienced developer persona spot-checks Command Reference pages for signature, return type, and example correctness
  4. Technical writer persona reviews User Guide for undefined terms and concepts used before introduction
  5. AI review findings appear in the same Finding/report pipeline as structural checks (same format, same severity levels, same output modes)
**Plans**: 2 plans

Plans:
- [ ] 04-01-PLAN.md — Persona definitions, Pydantic schemas, reviewer engine, unit tests with mocked API
- [ ] 04-02-PLAN.md — AI checker registry integration, CLI review subcommand, integration tests

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and Structural Checks | 3/3 | Complete | 2026-03-14 |
| 2. Cross-Reference Validation | 3/3 | Complete   | 2026-03-15 |
| 3. Auto-Fix | 1/2 | In Progress|  |
| 4. AI Persona Reviews | 0/2 | Not started | - |

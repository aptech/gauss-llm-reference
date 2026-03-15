# Roadmap: GAUSS Documentation QA System

## Milestones

- ✅ **v1.0 GAUSS Doc QA** -- Phases 1-4 (shipped 2026-03-15)
- **v1.1 Glossary & Deep Validation** -- Phases 5-7 (in progress)

## Phases

<details>
<summary>v1.0 GAUSS Doc QA (Phases 1-4) -- SHIPPED 2026-03-15</summary>

- [x] Phase 1: Foundation and Structural Checks (3/3 plans) -- completed 2026-03-14
- [x] Phase 2: Cross-Reference Validation (3/3 plans) -- completed 2026-03-15
- [x] Phase 3: Auto-Fix (2/2 plans) -- completed 2026-03-15
- [x] Phase 4: AI Persona Reviews (2/2 plans) -- completed 2026-03-15

</details>

### v1.1 Glossary & Deep Validation

- [ ] **Phase 5: Terminology Glossary** - Canonical glossary definition and terminology enforcement across RST corpus
- [ ] **Phase 6: Cross-Reference Frequency Ranking** - Rank Command Reference functions by reference count and produce top-N target list
- [x] **Phase 7: Top-N Deep Validation** - Deep structural and AI-assisted validation of most-referenced function pages (completed 2026-03-15)

## Phase Details

### Phase 5: Terminology Glossary
**Goal**: Users can enforce consistent terminology across the entire documentation corpus using a canonical glossary
**Depends on**: Phase 4 (v1.0 complete -- existing checker/report infrastructure)
**Requirements**: GLOS-01, GLOS-02, GLOS-03, GLOS-04
**Success Criteria** (what must be TRUE):
  1. User can author a YAML glossary file defining preferred terms, aliases, and deviations
  2. Running scan with --glossary flag produces findings for every non-canonical term with file, line, and suggested replacement
  3. Glossary findings appear in terminal, JSON, and Markdown reports with standard severity levels
  4. Glossary checker produces zero false positives on already-canonical text
**Plans**: 2 plans

Plans:
- [x] 05-01-PLAN.md -- Glossary model, YAML loader, GlossaryChecker, and unit tests
- [ ] 05-02-PLAN.md -- CLI --glossary integration and end-to-end report tests

### Phase 6: Cross-Reference Frequency Ranking
**Goal**: Users can identify the most-referenced functions in the documentation to prioritize validation effort, using both doc cross-references and blog post mentions as signals
**Depends on**: Phase 4 (v1.0 complete -- uses Sphinx cross-reference data)
**Requirements**: FREQ-01, FREQ-02, FREQ-03
**Success Criteria** (what must be TRUE):
  1. User can run frequency ranking and see every Command Reference function ranked by cross-reference count
  2. Frequency report is available in terminal, JSON, and Markdown formats
  3. User can specify top-N (default 100) to produce a target list file consumed by deep validation
**Plans**: 2 plans

Plans:
- [ ] 06-01-PLAN.md -- Frequency models, cross-ref counter, blog scraper, scorer, report formatters, and unit tests
- [ ] 06-02-PLAN.md -- CLI freq subcommand with --top-n, --output-targets, --no-blog options and CLI integration tests

### Phase 7: Top-N Deep Validation
**Goal**: Users can deeply validate the most important function pages for signature completeness, example quality, and documentation accuracy
**Depends on**: Phase 6 (top-N target list)
**Requirements**: DEEP-01, DEEP-02, DEEP-03, DEEP-04
**Success Criteria** (what must be TRUE):
  1. User can run deep-validate and see per-function pass/fail for: complete signature, non-trivial examples, return type documented, See Also present
  2. AI-assisted review flags suspicious example code (wrong function names, impossible parameters, misleading comments) for each top-N function
  3. Validation report shows per-function drill-down with individual check results across all deep checks
  4. CLI deep-validate subcommand accepts --top-n flag and runs the full frequency ranking + deep validation pipeline end-to-end
**Plans**: 2 plans

Plans:
- [x] 07-01-PLAN.md -- Deep validation models, structural page checker (4 checks), and report formatters
- [ ] 07-02-PLAN.md -- AI-assisted example verification and CLI deep-validate subcommand

## Progress

**Execution Order:** Phase 5 and Phase 6 are independent; Phase 7 depends on Phase 6.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation and Structural Checks | v1.0 | 3/3 | Complete | 2026-03-14 |
| 2. Cross-Reference Validation | v1.0 | 3/3 | Complete | 2026-03-15 |
| 3. Auto-Fix | v1.0 | 2/2 | Complete | 2026-03-15 |
| 4. AI Persona Reviews | v1.0 | 2/2 | Complete | 2026-03-15 |
| 5. Terminology Glossary | v1.1 | 1/2 | In progress | - |
| 6. Cross-Reference Frequency Ranking | v1.1 | 2/2 | Complete | 2026-03-15 |
| 7. Top-N Deep Validation | 2/2 | Complete   | 2026-03-15 | - |

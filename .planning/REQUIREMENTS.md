# Requirements: GAUSS Documentation QA System

**Defined:** 2026-03-15
**Core Value:** Every function in the Command Reference must have an accurate signature, correct examples, and be reachable from navigation

## v1.1 Requirements

### Glossary

- [x] **GLOS-01**: User can define a canonical glossary file (YAML) with preferred terms, aliases, and common deviations
- [x] **GLOS-02**: Terminology scanner checker flags non-canonical terms across RST files with file path, line, and suggested replacement
- [ ] **GLOS-03**: Glossary checker integrates into existing Finding/report pipeline (same severity, format, output modes)
- [ ] **GLOS-04**: CLI scan command accepts --glossary flag to enable terminology checking with a glossary file path

### Frequency Ranking

- [ ] **FREQ-01**: Cross-reference frequency ranker counts how many times each Command Reference function is referenced across all docs
- [ ] **FREQ-02**: Frequency report outputs ranked list of functions with reference counts in terminal, JSON, and Markdown formats
- [ ] **FREQ-03**: Top-N selection (default N=100) produces a target list for deep validation

### Deep Validation

- [ ] **DEEP-01**: Deep page validator checks top-N function pages for: complete signature (all params documented), non-trivial examples (not just syntax), return type documented, See Also present
- [ ] **DEEP-02**: AI-assisted validation uses Claude to verify example code correctness and flag suspicious patterns (wrong function names, impossible parameter combinations, misleading comments)
- [ ] **DEEP-03**: Validation report shows per-function pass/fail status across all deep checks with drill-down details
- [ ] **DEEP-04**: CLI deep-validate subcommand runs frequency ranking + deep validation pipeline with --top-n flag (default 100)

## Future Requirements (v1.2+)

- **GLOS-05**: Auto-fix for non-canonical terms (leaf-text-only safe replacement)
- **GLOS-06**: Glossary builder scans corpus to auto-generate initial glossary from frequent terms
- **DIFF-01**: Diff-mode checks only files changed since last run
- **FIXR-05**: :doc: and :ref: auto-fix (extend beyond :func:)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Glossary auto-fix | Deferred to v1.2 -- want to validate glossary file format first |
| Glossary auto-generation | Deferred to v1.2 -- manual curation more reliable for v1 |
| Diff-mode | Workflow efficiency, not doc quality -- v1.2 |
| Feedback widget | Requires deployment infrastructure |
| Screenshot inventory | Separate effort |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GLOS-01 | Phase 5 | Complete |
| GLOS-02 | Phase 5 | Complete |
| GLOS-03 | Phase 5 | Pending |
| GLOS-04 | Phase 5 | Pending |
| FREQ-01 | Phase 6 | Pending |
| FREQ-02 | Phase 6 | Pending |
| FREQ-03 | Phase 6 | Pending |
| DEEP-01 | Phase 7 | Pending |
| DEEP-02 | Phase 7 | Pending |
| DEEP-03 | Phase 7 | Pending |
| DEEP-04 | Phase 7 | Pending |

**Coverage:**
- v1.1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0

---
*Requirements defined: 2026-03-15*
*Last updated: 2026-03-15 after roadmap creation*

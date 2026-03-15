# Requirements: GAUSS Documentation QA System

**Defined:** 2026-03-15
**Core Value:** Every function in the Command Reference must have an accurate signature, correct examples, and be reachable from navigation

## v1.2 Requirements

### Diff Mode

- [ ] **DIFF-01**: User can run scan in diff-mode that only checks RST files modified since a given date or SVN revision
- [ ] **DIFF-02**: Diff-mode produces the same Finding/report output as full scan but only for changed files
- [ ] **DIFF-03**: CLI scan accepts --since flag (date or SVN revision) to enable diff-mode

### Extended Auto-Fix

- [x] **EFIX-01**: Auto-fix resolves broken :doc: references by fuzzy-matching against known doc names in env.all_docs
- [x] **EFIX-02**: Auto-fix resolves broken :ref: references by fuzzy-matching against std domain labels
- [x] **EFIX-03**: Extended auto-fix uses same leaf-text-only safety constraint and dry-run default as :func: fixer

### Glossary Auto-Fix

- [x] **GFIX-01**: Glossary auto-fix replaces non-canonical terms with canonical equivalents using leaf-text-only safe editing
- [ ] **GFIX-02**: CLI fix accepts --glossary flag to apply terminology corrections (dry-run default)
- [x] **GFIX-03**: Glossary auto-fix skips terms inside code blocks, directives, and table structures

### Glossary Generation

- [ ] **GGEN-01**: Glossary generator scans corpus to extract frequently-used terms and group by semantic similarity
- [ ] **GGEN-02**: Generator outputs a draft YAML glossary file that the user can curate
- [ ] **GGEN-03**: CLI glossary-gen subcommand produces the draft glossary from a docs directory

## Future Requirements (v2.0+)

- **CI-01**: CI integration for automated doc checks on commit
- **FEED-01**: Feedback widget embedded in Sphinx theme

## Out of Scope

| Feature | Reason |
|---------|--------|
| CI integration | Deferred to v2.0 — needs build system integration |
| Feedback widget | Requires deployment infrastructure |
| Screenshot inventory | Separate effort |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DIFF-01 | Phase 9 | Pending |
| DIFF-02 | Phase 9 | Pending |
| DIFF-03 | Phase 9 | Pending |
| EFIX-01 | Phase 8 | Complete |
| EFIX-02 | Phase 8 | Complete |
| EFIX-03 | Phase 8 | Complete |
| GFIX-01 | Phase 8 | Complete |
| GFIX-02 | Phase 8 | Pending |
| GFIX-03 | Phase 8 | Complete |
| GGEN-01 | Phase 10 | Pending |
| GGEN-02 | Phase 10 | Pending |
| GGEN-03 | Phase 10 | Pending |

**Coverage:**
- v1.2 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-03-15*
*Last updated: 2026-03-15 after roadmap creation*

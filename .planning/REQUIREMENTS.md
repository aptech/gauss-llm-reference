# Requirements: GAUSS Documentation QA System

**Defined:** 2026-03-14
**Core Value:** Every function in the Command Reference must have an accurate signature, correct examples, and be reachable from navigation

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Foundation

- [x] **FOUN-01**: RST files parsed via docutils AST (not regex) with doc type classification (function, operator, index, guide, fragment)
- [ ] **FOUN-02**: Sphinx environment loads with custom GAUSS domain for cross-reference resolution
- [x] **FOUN-03**: Finding dataclass with severity levels (ERROR/WARNING/INFO), file path, line number, category, message
- [ ] **FOUN-04**: CLI entry point with subcommands for individual checks and full scan

### Structural Checks

- [ ] **STRC-01**: Code block presence check — every Command Reference page has at least one literal_block node
- [ ] **STRC-02**: Code block non-empty check — no literal_block nodes with whitespace-only content
- [ ] **STRC-03**: Broken cross-reference detection — all :func:, :doc:, :ref: links resolve through GAUSS domain
- [ ] **STRC-04**: Orphan page detection — RST files not in any toctree (respecting :orphan: directive and include fragments)
- [ ] **STRC-05**: Section structure validation — Command Reference pages have required sections (Purpose/Format/Examples)
- [ ] **STRC-06**: Function signature completeness — function directives have parameters and return type documented
- [ ] **STRC-07**: Function coverage check — every Command Reference function name appears in at least one code example somewhere in the docs
- [ ] **STRC-08**: See Also validation — seealso links point to existing function pages

### Auto-Fix

- [ ] **FIXR-01**: Auto-fix for broken internal links where target can be unambiguously determined
- [ ] **FIXR-02**: Auto-fix runs in dry-run mode by default, showing proposed changes without applying
- [ ] **FIXR-03**: Auto-fix only modifies leaf text nodes, never tables or directive structures
- [ ] **FIXR-04**: Sphinx build verification available after auto-fix to confirm no RST corruption

### AI Reviews

- [ ] **AIRV-01**: Batch AI persona reviews via Claude API with structured binary rubrics (not free-text)
- [ ] **AIRV-02**: New GAUSS user persona reviews Getting Started and tutorials — "Where did you get confused?"
- [ ] **AIRV-03**: Experienced developer persona reviews Command Reference spot-check — "Is the signature, return type, and example correct?"
- [ ] **AIRV-04**: Technical writer persona reviews User Guide — "Are concepts introduced before used? Undefined terms?"
- [ ] **AIRV-05**: Persona review findings integrate into the same Finding/report system as structural checks

### Reporting

- [ ] **REPT-01**: Terminal output with severity colors via rich library
- [ ] **REPT-02**: JSON report output for machine processing
- [ ] **REPT-03**: Markdown report output for sharing and review
- [ ] **REPT-04**: Summary counts by category and severity at top of every report

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Terminology

- **TERM-01**: YAML-based canonical glossary with preferred/rejected term pairs
- **TERM-02**: Terminology consistency checking via rapidfuzz in text nodes (excluding code blocks)
- **TERM-03**: Auto-fix for terminology deviations

### Deep Validation

- **DEEP-01**: Cross-reference frequency ranking to identify top-N most-linked functions
- **DEEP-02**: Top-N function deep validation — comprehensive AI checks on signature accuracy, example correctness, parameter completeness
- **DEEP-03**: Persona for MATLAB/R migrator reviews migration-relevant content

### Optimization

- **OPTM-01**: Diff-mode — run checks only on SVN-modified files
- **OPTM-02**: Caching of Sphinx environment between runs

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web dashboard | Over-engineering for small team; markdown reports sufficient |
| CI/CD integration | System needs to prove value in manual runs first |
| Real-time file watching | Docs edited in batches, not continuously |
| Grammar/style linting | Noisy for technical docs; AI personas handle prose quality |
| PDF/HTML output validation | Focus is on RST source quality |
| GAUSS runtime example verification | Very high complexity (requires tgauss integration) |
| Feedback widget (Tier 4) | Requires deployment infrastructure |
| Screenshot inventory | Separate manual effort, not scriptable |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUN-01 | Phase 1 | Complete |
| FOUN-02 | Phase 2 | Pending |
| FOUN-03 | Phase 1 | Complete |
| FOUN-04 | Phase 1 | Pending |
| STRC-01 | Phase 1 | Pending |
| STRC-02 | Phase 1 | Pending |
| STRC-03 | Phase 2 | Pending |
| STRC-04 | Phase 2 | Pending |
| STRC-05 | Phase 1 | Pending |
| STRC-06 | Phase 1 | Pending |
| STRC-07 | Phase 2 | Pending |
| STRC-08 | Phase 2 | Pending |
| FIXR-01 | Phase 3 | Pending |
| FIXR-02 | Phase 3 | Pending |
| FIXR-03 | Phase 3 | Pending |
| FIXR-04 | Phase 3 | Pending |
| AIRV-01 | Phase 4 | Pending |
| AIRV-02 | Phase 4 | Pending |
| AIRV-03 | Phase 4 | Pending |
| AIRV-04 | Phase 4 | Pending |
| AIRV-05 | Phase 4 | Pending |
| REPT-01 | Phase 1 | Pending |
| REPT-02 | Phase 1 | Pending |
| REPT-03 | Phase 1 | Pending |
| REPT-04 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 25 total
- Mapped to phases: 25
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-14*
*Last updated: 2026-03-14 after roadmap creation*

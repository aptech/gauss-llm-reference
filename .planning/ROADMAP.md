# Roadmap: GAUSS Documentation QA System

## Milestones

- ✅ **v1.0 GAUSS Doc QA** -- Phases 1-4 (shipped 2026-03-15)
- ✅ **v1.1 Glossary & Deep Validation** -- Phases 5-7 (shipped 2026-03-15)
- 🚧 **v1.2 Polish & Efficiency** -- Phases 8-10 (in progress)

## Phases

<details>
<summary>✅ v1.0 GAUSS Doc QA (Phases 1-4) -- SHIPPED 2026-03-15</summary>

- [x] Phase 1: Foundation and Structural Checks (3/3 plans) -- completed 2026-03-14
- [x] Phase 2: Cross-Reference Validation (3/3 plans) -- completed 2026-03-15
- [x] Phase 3: Auto-Fix (2/2 plans) -- completed 2026-03-15
- [x] Phase 4: AI Persona Reviews (2/2 plans) -- completed 2026-03-15

</details>

<details>
<summary>✅ v1.1 Glossary & Deep Validation (Phases 5-7) -- SHIPPED 2026-03-15</summary>

- [x] Phase 5: Terminology Glossary (2/2 plans) -- completed 2026-03-15
- [x] Phase 6: Cross-Reference Frequency Ranking (2/2 plans) -- completed 2026-03-15
- [x] Phase 7: Top-N Deep Validation (2/2 plans) -- completed 2026-03-15

</details>

### v1.2 Polish & Efficiency

- [x] **Phase 8: Extended Auto-Fix** - Extend auto-fix to cover :doc:, :ref:, and glossary term corrections
- [x] **Phase 9: Diff Mode** - Incremental scanning of only changed RST files
- [x] **Phase 10: Glossary Generation** - Auto-generate draft glossary from corpus term frequency (completed 2026-03-15)

## Phase Details

### Phase 8: Extended Auto-Fix
**Goal**: Users can auto-fix broken :doc: and :ref: references and non-canonical glossary terms, not just :func: references
**Depends on**: Phase 3 (auto-fix engine), Phase 5 (glossary system)
**Requirements**: EFIX-01, EFIX-02, EFIX-03, GFIX-01, GFIX-02, GFIX-03
**Success Criteria** (what must be TRUE):
  1. Running `fix` on a file with a broken :doc: reference resolves it to the correct doc name via fuzzy match
  2. Running `fix` on a file with a broken :ref: reference resolves it to the correct label via fuzzy match
  3. Running `fix --glossary` on a file with non-canonical terms replaces them with canonical equivalents
  4. All extended auto-fixes skip content inside code blocks, directives, and table structures (leaf-text-only safety)
  5. All extended auto-fixes default to dry-run and require explicit confirmation to write changes
**Plans:** 2 plans

Plans:
- [x] 08-01-PLAN.md -- Extend resolver for :doc:/:ref: fuzzy matching + glossary fixer module
- [x] 08-02-PLAN.md -- Wire extended fixes and glossary fixer into CLI fix subcommand

### Phase 9: Diff Mode
**Goal**: Users can run incremental scans that only check files changed since a given point in time, avoiding full-corpus re-scans
**Depends on**: Phase 1 (scan infrastructure)
**Requirements**: DIFF-01, DIFF-02, DIFF-03
**Success Criteria** (what must be TRUE):
  1. Running `scan --since 2026-03-01` only checks RST files modified after that date
  2. Running `scan --since r12345` only checks RST files changed since SVN revision 12345
  3. Diff-mode output uses the same Finding model and report format as full scan (terminal, JSON, Markdown)
**Plans:** 1 plan

Plans:
- [x] 09-01-PLAN.md -- Diff filtering module + CLI --since wiring

### Phase 10: Glossary Generation
**Goal**: Users can auto-generate a draft glossary from corpus analysis instead of manually curating one from scratch
**Depends on**: Phase 5 (glossary system)
**Requirements**: GGEN-01, GGEN-02, GGEN-03
**Success Criteria** (what must be TRUE):
  1. Running `glossary-gen` on a docs directory extracts frequently-used terms and groups them by semantic similarity
  2. The output is a draft YAML glossary file in the same format as the canonical glossary, ready for manual curation
  3. The `glossary-gen` subcommand is available in the CLI and accepts a docs directory path
**Plans:** 1/1 plans complete

Plans:
- [ ] 10-01-PLAN.md -- Term extraction, grouping module, and CLI glossary-gen subcommand

## Progress

**Execution Order:** 8 -> 9 -> 10

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation and Structural Checks | v1.0 | 3/3 | Complete | 2026-03-14 |
| 2. Cross-Reference Validation | v1.0 | 3/3 | Complete | 2026-03-15 |
| 3. Auto-Fix | v1.0 | 2/2 | Complete | 2026-03-15 |
| 4. AI Persona Reviews | v1.0 | 2/2 | Complete | 2026-03-15 |
| 5. Terminology Glossary | v1.1 | 2/2 | Complete | 2026-03-15 |
| 6. Cross-Reference Frequency Ranking | v1.1 | 2/2 | Complete | 2026-03-15 |
| 7. Top-N Deep Validation | v1.1 | 2/2 | Complete | 2026-03-15 |
| 8. Extended Auto-Fix | v1.2 | 2/2 | Complete | 2026-03-15 |
| 9. Diff Mode | v1.2 | 1/1 | Complete | 2026-03-15 |
| 10. Glossary Generation | 1/1 | Complete   | 2026-03-15 | - |

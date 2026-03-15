# Retrospective

## Milestone: v1.0 — GAUSS Doc QA

**Shipped:** 2026-03-15
**Phases:** 4 | **Plans:** 10 | **Tasks:** 20

### What Was Built
- docutils-based RST parser with 6-rule doc type classifier
- Structural checkers (code blocks, sections, signatures) via BaseChecker registry
- Sphinx dummy builder integration for cross-reference validation
- 4 Sphinx-mode checkers (links, orphans, coverage, seealso)
- Auto-fix engine with fuzzy matching, leaf-text-only safety, Sphinx verification
- AI persona review system with binary rubrics via Claude API structured outputs
- Click CLI with scan, check-refs, fix, review subcommands
- Terminal/JSON/Markdown report formatters

### What Worked
- Wave-based parallel execution let independent plans run concurrently (Wave 1 of Phase 2 ran Sphinx loader and 4 checkers in parallel)
- BaseChecker registry pattern made adding new checkers trivial — each checker is a self-registering class
- Lazy import pattern for optional dependencies (Sphinx, anthropic) kept CLI responsive for non-dependent commands
- Binary rubric approach for AI reviews eliminated noise — pass/fail per concrete criterion, severity set by config not by Claude

### What Was Inefficient
- VALIDATION.md files created manually by orchestrator diverged from plan test file names (draft → actual)
- One-liner fields not populated in SUMMARY.md files, reducing value for milestone completion extraction

### Patterns Established
- `BaseChecker.register_checker()` for pluggable checker modules
- `requires_sphinx = True` / `requires_api = True` flags for conditional checker loading
- Lazy imports inside function bodies for heavy optional dependencies
- Leaf-text-only constraint for safe RST modifications
- Finding dataclass as universal report unit across all checker types

### Key Lessons
- docutils handles `.. function::` directives gracefully even without Sphinx (system_message nodes)
- The custom GAUSS domain uses casefold() for matching — all validation must match this behavior
- RST auto-fix must operate on raw text lines, not docutils tree (no faithful round-trip)

### Cost Observations
- Model mix: ~80% opus (execution), ~20% sonnet (verification/checking)
- Sessions: 1 continuous session
- Notable: All 4 phases planned and executed in a single conversation

---

## Milestone: v1.1 — Glossary & Deep Validation

**Shipped:** 2026-03-15
**Phases:** 3 | **Plans:** 6 | **Tasks:** 11

### What Was Built
- YAML-based canonical glossary with terminology scanner (word-boundary matching, code block skipping)
- Cross-reference frequency ranker with dual data sources (doc xrefs + blog scraping)
- Top-N target list export for pipeline integration between commands
- Deep structural validation (4 checks per function page)
- AI-assisted example code verification via Claude API
- CLI deep-validate subcommand with full pipeline orchestration

### What Worked
- Skipping research for v1.1 saved time — domain was well-understood from v1.0
- Blog scraping with graceful degradation (`--no-blog`) gave flexibility without fragility
- Deep validation as a separate module (not Finding-based) was the right call — per-function pass/fail is a different abstraction
- Stdlib-only blog scraper (urllib + html.parser) avoided new dependencies

### What Was Inefficient
- ROADMAP.md plan checkboxes got out of sync with actual completion (Phase 5/6 plans shown as unchecked despite summaries existing)

### Patterns Established
- Dual-signal frequency ranking (weighted combination of internal + external signals)
- `--output-targets` file as pipeline glue between commands
- Deep validation module with DeepCheckType enum for extensible check types
- `--no-ai` flag pattern for fast structural-only runs

### Key Lessons
- N=100 is a good sweet spot for deep validation — covers high-traffic functions without overwhelming output
- Blog scraping is useful but noisy — weighting it at 0.3 vs 0.7 for doc xrefs was appropriate

### Cost Observations
- Model mix: ~80% opus (execution), ~20% sonnet (verification)
- Sessions: continued from v1.0 in same conversation
- Notable: All 3 phases completed in ~30 minutes wall time

---

## Cross-Milestone Trends

| Metric | v1.0 | v1.1 | Cumulative |
|--------|------|------|------------|
| Phases | 4 | 3 | 7 |
| Plans | 10 | 6 | 16 |
| Tasks | 20 | 11 | 31 |
| Source LOC | 2,307 | 1,433 | 3,740 |
| Test LOC | 2,455 | 1,923 | 4,378 |
| Test/Source Ratio | 1.06 | 1.34 | 1.17 |
| Commits | 44 | 24 | 68 |

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

## Cross-Milestone Trends

| Metric | v1.0 |
|--------|------|
| Phases | 4 |
| Plans | 10 |
| Tasks | 20 |
| Source LOC | 2,307 |
| Test LOC | 2,455 |
| Test/Source Ratio | 1.06 |
| Commits | 44 |

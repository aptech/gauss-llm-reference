# Milestones

## v1.1 Glossary & Deep Validation (Shipped: 2026-03-15)

**Phases completed:** 3 phases, 6 plans, 11 tasks
**Stats:** 1,433 new LOC source + 1,923 new LOC tests, 39 files, 24 commits
**Cumulative:** 3,740 LOC source + 4,378 LOC tests

**Key accomplishments:**
1. Canonical glossary system — YAML glossary file with terminology scanner that flags non-canonical terms across RST files with word-boundary matching and code block skipping
2. Cross-reference frequency ranker — counts doc cross-refs (0.7 weight) + scrapes aptech.com/blog mentions (0.3 weight) for real-world usage signal
3. Top-N target list export — `--output-targets` writes ranked function names for downstream deep validation consumption
4. Deep structural validation — 4 checks per function page (signature completeness, non-trivial examples, return type, See Also)
5. AI-assisted example verification — Claude API checks example code for wrong function names, impossible parameters, misleading comments
6. Full deep-validate CLI pipeline — frequency ranking → structural checks → AI checks → per-function drill-down report

---

## v1.0 GAUSS Doc QA (Shipped: 2026-03-15)

**Phases completed:** 4 phases, 10 plans, 20 tasks
**Stats:** 2,307 LOC source + 2,455 LOC tests (Python), 97 files, 44 commits

**Key accomplishments:**
1. docutils-based RST parser with doc type classifier (function/operator/guide/index/fragment) and file inventory scanner
2. Structural checkers for code block presence, required sections, and function signature completeness
3. Sphinx dummy builder integration for cross-reference validation (broken links, orphan pages, function coverage, See Also)
4. Auto-fix engine with fuzzy-match resolver, leaf-text-only safety constraint, and Sphinx build verification
5. AI persona review system with binary rubrics (Newcomer, Expert, Writer) via Claude API structured outputs
6. Full CLI with scan, check-refs, fix, and review subcommands plus terminal/JSON/Markdown report formatters

---


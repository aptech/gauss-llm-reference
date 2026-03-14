# Feature Landscape

**Domain:** Documentation QA automation for Sphinx RST sources
**Researched:** 2026-03-14
**Confidence:** HIGH (verified against actual doc corpus and Sphinx configuration)

## Table Stakes

Features the system must have to deliver value. Missing any makes the system incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Broken cross-reference detection** | `:func:` links to nonexistent pages are invisible until a user clicks. ~1,400 function pages with cross-refs via custom GAUSS domain | Medium | Requires Sphinx environment to resolve through the custom GAUSS domain. Cannot use regex -- `default_role='any'` means bare backticks also resolve |
| **Code block presence check** | Every Command Reference page must have at least one example. Missing examples = useless reference | Low | Docutils AST traversal for `literal_block` nodes. The corpus uses `::` literal blocks (not `.. code-block::`), both produce the same node type |
| **Code block non-empty check** | Empty code blocks render as blank boxes -- worse than missing | Low | Check `literal_block` node text content is non-whitespace |
| **Orphan page detection** | RST files not in any toctree are unreachable from navigation | Medium | Requires recursive toctree graph from root. Two-level structure: index -> letter pages -> function pages. Must also handle `:orphan:` directive and `include/` fragments |
| **Structured section validation** | Command Reference pages must follow template: Purpose, Format, Examples. Pages missing required sections are incomplete | Medium | Doc type classification first (function vs operator vs index vs guide), then type-specific section rules |
| **Terminology/glossary consistency** | Inconsistent naming ("dataframe" vs "data frame", "GAUSS" vs "Gauss") confuses users and LLMs | Medium | YAML glossary + rapidfuzz. Must exclude code blocks from matching. Must handle domain-specific context (dataset vs dataframe are different things in GAUSS) |
| **Report generation** | Machine-readable (JSON) + human-readable (terminal) output with severity tiers | Low | rich for terminal, json for files. Summary counts at top. Group by category not by file |
| **Severity classification** | ERROR/WARNING/INFO tiers. Without this, a 500-finding report is unactionable | Low | Built into Finding dataclass. Reports show errors first |

## Differentiators

Features that add significant value beyond basic linting.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **AI persona reviews** | 4 personas (newcomer, experienced dev, MATLAB/R migrator, API-reference-checker) reviewing 4 doc sections. Catches qualitative issues no linter finds | Medium | ~16 review passes via Claude API. Strict binary rubric per persona (5-8 checks). Structured output, not free-text |
| **Top-N function deep validation** | Cross-reference frequency identifies most-linked functions. Deep-validate those first for maximum impact | Medium | Build cross-ref frequency index, then comprehensive AI checks on top-20 (signature accuracy, example correctness, parameter completeness) |
| **Auto-fix for safe issues** | Automatically fix terminology deviations, obvious broken links, whitespace issues | Medium | Conservative: only fix within leaf text nodes, never in tables/directives. Dry-run mode default. Sphinx build verification after |
| **Function signature completeness** | Every `:param:` should have a `:type:`, every `.. function::` should have `:return:` and `:rtype:` | Low | Docutils AST check on field_list nodes inside function directives |
| **Cross-reference frequency ranking** | Rank functions by reference count. Proxy for importance without analytics | Low | Count `:func:` references, weight by section diversity |
| **See Also validation** | Verify `.. seealso::` links point to existing functions | Low | Simple cross-ref subset check, catches stale references |
| **Function coverage check** | Every Command Reference function appears in at least one working example | Medium | Cross-reference function names from filenames against code block contents |
| **Diff-mode (changed files only)** | Run checks only on files modified since last run (SVN-aware) | Medium | `svn diff --summarize` to scope checks. Note: link validation must still run globally |

## Anti-Features

Features to explicitly NOT build.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Interactive web dashboard** | Over-engineering for a team of 1-3 people. Building and maintaining a web UI is a separate project | Markdown/JSON reports viewable in any editor |
| **CI/CD integration** | Premature. System needs to prove value in manual runs first | Run manually. Add CI hooks in a future milestone |
| **Real-time file watching** | Docs are edited in batches, not continuously | Batch execution on demand |
| **Grammar/style linting** | Noisy for technical docs, subjective. Tools like vale exist but need heavy config | Let AI persona reviews handle prose quality with domain context |
| **PDF/HTML output validation** | Out of scope per PROJECT.md. Rendering issues are Sphinx theme problems | Focus on RST source quality |
| **Full HTML Sphinx build output** | Slow, unnecessary. We need the Sphinx environment data, not rendered HTML | Use Sphinx's Python API with a dummy/null builder to get resolved references |
| **Example output verification via GAUSS runtime** | Very high complexity (requires running GAUSS code). Would need `tgauss -b` integration | Consider for a future milestone. AI deep validation can partially cover this |
| **Multi-language support** | GAUSS docs are English-only | Do not abstract for i18n |

## Feature Dependencies

```
Sphinx environment load
  --> Broken cross-ref detection
  --> Orphan page detection
  --> Cross-ref frequency ranking
      --> Top-N function identification
          --> Deep validation of top functions

Docutils RST parsing (fast mode)
  --> Code block checks
  --> Function signature completeness
  --> Section structure validation
  --> Terminology consistency (text node matching)

Terminology glossary (YAML)
  --> Terminology consistency checking
      --> Auto-fix (terminology)

Detection results
  --> Auto-fix (only fix what is detected)

All checks --> Report generation (Finding objects)

Report generation
  --> AI persona reviews (personas can reference structural findings)
```

## MVP Recommendation

**Prioritize (Phase 1):**
1. **Code block presence + non-empty checks** -- Low complexity, immediate value, docutils-only
2. **Function signature completeness** -- Low complexity, catches common doc omissions
3. **Structured section validation** -- Ensures every function page has Purpose, Format, Examples
4. **Severity classification + report generation** -- Must ship with first checks or findings are unactionable

**Phase 2:**
5. **Broken cross-reference detection** -- Medium complexity, highest-impact structural check, requires Sphinx env
6. **Orphan page detection** -- Falls out naturally once Sphinx environment is loaded
7. **Terminology consistency** -- Requires curated glossary, start small (10-15 terms)

**Defer to Phase 3+:**
- **AI persona reviews** -- Structural checks should establish a baseline first. AI reviews are most valuable after structural issues are fixed
- **Auto-fix** -- Build read-only detection first, add fixes once detection confidence is established
- **Top-N deep validation** -- Depends on cross-ref frequency analysis and AI infrastructure
- **Diff-mode** -- Optimization. Full scans on 1,700 files are fast enough initially

## Sources

- Direct inspection of `~/svn/gxmldoc/docs/abs.rst`, `olsmt.rst`, `ols.rst` (representative Command Reference pages)
- Sphinx conf.py analysis: custom GAUSS domain, `primary_domain='gauss'`, `default_role='any'`
- Cross-reference patterns: `:func:`, `:doc:`, `:ref:` roles confirmed via grep across corpus
- Toctree structure: letter index pages (a.rst-z.rst) link to individual function pages
- Include directory: `docs/include/` contains fragments for `.. include::` directives
- PROJECT.md requirements and scope

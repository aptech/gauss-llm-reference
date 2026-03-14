# Domain Pitfalls

**Domain:** Documentation QA system for Sphinx RST technical reference (~1,700 files, custom GAUSS domain)
**Researched:** 2026-03-14

## Critical Pitfalls

Mistakes that cause rewrites or major issues.

### Pitfall 1: Treating RST as Plain Text Instead of Parsing the Doctree

**What goes wrong:** QA scripts use regex or line-by-line string matching to find structural issues. Works for 80% of cases, then silently produces false positives/negatives on the other 20%: include directives, substitutions, nested directives, multi-line field lists, and indentation-sensitive blocks.

**Why it happens:** Regex is fast to write. docutils parsing feels heavyweight for "simple" checks.

**Consequences:** False positives erode trust ("this tool cries wolf"). False negatives let real issues slip through. Each new edge case requires another regex hack.

**Prevention:**
- Use `docutils.parsers.rst.Parser` to parse into a doctree for all structural checks.
- Reserve regex only for content-level checks within already-parsed text nodes (e.g., terminology matching within paragraph text).
- Both `::` literal blocks and `.. code-block::` directives produce `literal_block` nodes in the doctree -- another reason to parse rather than regex.

**Detection:** If you find yourself writing regex that handles "but what if it's indented" or "but what if there's a blank line," you've hit this.

---

### Pitfall 2: Ignoring the Custom GAUSS Sphinx Domain

**What goes wrong:** The QA system treats all RST as standard Sphinx. But this project uses a custom `GAUSSDomain` (in `docs/util/GAUSSDomain.py`, registered as primary domain via `primary_domain = 'gauss'` in conf.py). Cross-reference checks that expect standard `:py:func:` resolution will misinterpret or miss references.

**Why it happens:** Most documentation QA examples target standard Sphinx Python docs. The custom domain is loaded in `conf.py`'s `setup()` function, not declared in `extensions`.

**Consequences:** Cross-reference validation reports valid refs as broken. Function signature parsing misidentifies GAUSS-style signatures (`{y1, y2} = func(x)` with curly-brace return syntax, parsed by custom `py_sig_re` in GAUSSDomain.py). The entire link-checking tier becomes unreliable.

**Prevention:**
- Use Sphinx's Python API (`sphinx.application.Sphinx`) to load the full build environment, which includes the custom GAUSS domain. This gives you resolved references through the real resolution pipeline.
- Before building cross-reference checks, read `GAUSSDomain.py` and `GAUSSRoles.py` to understand what roles and directives the domain registers.
- The `default_role = 'any'` setting means bare backtick references (`` `funcname` ``) also resolve through the domain -- regex scanning for `:func:` alone will miss these.

**Detection:** If your link checker reports `:func:` references as broken when Sphinx builds them fine, you've hit this.

---

### Pitfall 3: Auto-Fix Scripts That Corrupt RST Formatting

**What goes wrong:** Auto-fix scripts modify RST files but break indentation, directive nesting, or table alignment. RST is whitespace-sensitive: directive content must be indented, tables require exact column alignment, literal blocks depend on `::` plus indentation.

**Why it happens:** String-level find-and-replace doesn't understand RST structure. Fixing a terminology issue inside a table cell shifts column widths.

**Consequences:** Sphinx build breaks. Worse: Sphinx builds succeed but renders incorrectly (content falls out of a directive into body text). Invisible without diff review.

**Prevention:**
- Auto-fix only within leaf text nodes (paragraphs), never structural elements (tables, directives).
- Every auto-fix must be followed by Sphinx build verification of affected files.
- Dry-run mode is the default. Require explicit `--apply` flag.
- Whitelist "safe fix" categories. Refuse anything outside the whitelist.
- Before applying fixes, check `svn status` -- never auto-fix files with local modifications.

**Detection:** Run `sphinx-build` before and after auto-fixes. Any new warnings = corruption.

---

### Pitfall 4: AI Persona Reviews That Generate Noise Instead of Signal

**What goes wrong:** Batch AI reviews produce hundreds of "findings" that are stylistic preferences, not real issues. Team drowns in "consider adding more context" while genuine problems (wrong signature, broken example) get buried.

**Why it happens:** LLM prompts are too open-ended. "Review this documentation for quality" produces vague critique without a rubric.

**Consequences:** Team ignores AI review output after the first batch. The entire tier becomes waste.

**Prevention:**
- Define a strict rubric per persona. Each check must be binary (pass/fail) with a specific criterion:
  - "Does the Format section signature match the function directive?" (verifiable)
  - "Does each parameter in the signature appear in the parameter descriptions?" (verifiable)
  - "Does the example code call the function being documented?" (verifiable)
- NOT: "Is this documentation clear?" (subjective, unverifiable)
- Limit each persona to 5-8 specific, concrete checks.
- Require the AI to cite the specific line/section where issues occur.
- Classify findings as ERROR/WARNING/INFO. Only surface ERROR and WARNING in primary reports.
- Use structured output (tool_use or JSON schema) -- never free-text prose reviews.

**Detection:** If more than 30% of AI findings are disputed or ignored in review, the rubric is too loose.

---

### Pitfall 5: Validating Structure Without Validating Correctness

**What goes wrong:** The QA system confirms every function page has Purpose, Format, Examples -- but never checks whether content is correct. A page can pass all structural checks while having a wrong signature, incorrect parameter types, or an example that errors at runtime.

**Why it happens:** Structural checks are easy to automate. Correctness checks require ground truth.

**Consequences:** Docs look complete but are unreliable. Trust erodes faster from "looks right but is wrong" than from "obviously missing."

**Prevention:**
- Top-N function validation exists precisely for this. Treat it as equal to structural checks, not nice-to-have.
- For top-20 functions: extract `.. function::` signature, compare parameter count against `:param:` entries at minimum.
- For examples: if feasible, run snippets through `tgauss -b` to verify execution. Even "does it parse?" catches obvious issues.
- Cross-check parameter names between signature line and `:param:` entries.

## Moderate Pitfalls

### Pitfall 6: Orphan Detection That Doesn't Understand the Multi-Level Toctree

**What goes wrong:** Naive orphan checker looks for pages in the root toctree only. The GAUSS docs use multi-level toctrees: `index.rst` -> section pages -> letter pages (`a.rst`) -> function pages (`abs.rst`). A naive checker flags all 1,400+ function pages as orphans.

**Prevention:**
- Build the toctree graph recursively from `index.rst`. A page is orphaned only if unreachable from root through any chain.
- Check for `:orphan:` metadata directive (intentionally orphaned pages).
- Exclude `include/` directory (fragments, not standalone pages).

---

### Pitfall 7: Glossary Enforcement That's Too Aggressive

**What goes wrong:** Terminology checker flags legitimate uses. GAUSS has both `.dat` datasets and in-memory dataframes -- these are different things. "Matrix" vs "array" is also a real distinction (GAUSS has both).

**Prevention:**
- Build glossary collaboratively with domain experts, not from automated extraction.
- Include context rules: "dataset" is correct for `.dat` files, "dataframe" for in-memory typed data.
- Allow override annotations in RST (`.. terminology-ok: dataset`).
- Start with 10-15 terms and expand based on false positive feedback.
- Never flag terms inside code blocks or directive arguments.

---

### Pitfall 8: Cross-Reference Frequency as Sole Proxy for Importance

**What goes wrong:** Top-N list is derived from cross-reference frequency. But frequently referenced functions may be utilities in boilerplate (`zeros`, `ones`, `rndn`). The most important user-facing functions (`olsmt`, `loadd`, `plotXY`) may have fewer references because they're entry points.

**Prevention:**
- Use frequency as one signal, supplement with:
  - Functions appearing in Getting Started / User Guide (high-traffic entry points)
  - Known domain-critical functions (estimation, data loading, plotting)
- Weight "referenced from different doc sections" higher than "referenced many times from same section."

---

### Pitfall 9: Running QA Against Stale Doc Copies

**What goes wrong:** QA scripts operate on a snapshot, not the live SVN working copy. Results become stale. Auto-fixes conflict with concurrent edits.

**Prevention:**
- Always run against `~/svn/gxmldoc/docs/` directly.
- Before auto-fix, run `svn status` and warn on dirty working copy.
- Auto-fixes as a batch, review via `svn diff`, commit as single logical change.

---

### Pitfall 10: Report Fatigue from Unfilterable Output

**What goes wrong:** Single massive report with all findings at same visual weight. Can't distinguish 3 broken links from 47 missing Remarks sections.

**Prevention:**
- Severity tiers: ERROR, WARNING, INFO.
- Group by category (links, examples, terminology), not by file.
- Summary counts at top: "5 errors, 23 warnings, 112 info items."
- JSON output for programmatic filtering.
- Human-readable report shows errors and warnings only. Info in separate detail file.

## Minor Pitfalls

### Pitfall 11: Assuming All Function Pages Follow the Same Template

**What goes wrong:** Checks assume every top-level RST has Purpose/Format/Examples. But operator pages, index pages, and category pages have different structures.

**Prevention:** Classify pages by DocType before applying checks. Apply type-appropriate rulesets.

---

### Pitfall 12: Not Handling RST Include Fragments

**What goes wrong:** Files in `include/` (e.g., `plotattrremark.rst`) are checked as standalone pages and fail structural checks. Also flagged as orphans.

**Prevention:** Identify `include/` contents and exclude from standalone checks. Instead verify each fragment is `.. include::`'d from at least one real page.

---

### Pitfall 13: Code Block Detection Missing Bare Literal Blocks

**What goes wrong:** Checker looks only for `.. code-block::` directives. GAUSS docs predominantly use bare `::` literal blocks (as in `abs.rst`).

**Prevention:** Use docutils parsing. Both syntaxes produce `literal_block` nodes in the doctree. This is transparent when parsing the tree.

---

### Pitfall 14: Sphinx 9.x API Changes

**What goes wrong:** Code written against Sphinx 7.x or 8.x tutorials/examples may not work with Sphinx 9.1.0. The Sphinx internal API evolves between major versions.

**Prevention:** Pin Sphinx version in `pyproject.toml`. Test environment loading against the actual docs. The `sphinx.application.Sphinx` constructor interface is stable, but builder internals and environment attributes may shift.

**Confidence:** MEDIUM -- could not verify Sphinx 9.x specific API changes without WebSearch. Test early.

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Foundation (parser) | Regex-based parsing fails on nested RST | Use docutils parser from day one |
| Structural checks | Page type assumptions cause false positives | Classify DocType before checking |
| Link validation | Custom GAUSS domain breaks standard resolution | Load full Sphinx env with GAUSS domain |
| Orphan detection | Multi-level toctree causes mass false positives | Recursive graph traversal from root |
| Terminology | Domain-specific terms falsely flagged | Expert-curated glossary, start small |
| Auto-fix | RST formatting corruption | Leaf text nodes only, dry-run default, Sphinx build verify |
| AI reviews | Vague prompts produce noise | Strict binary rubric, 5-8 checks, structured output |
| Top-N selection | Frequency != importance | Supplement with section diversity and domain knowledge |
| Reports | Unstructured output causes fatigue | Severity tiers, category grouping, summary counts |
| All phases | Stale data from copied docs | Always target live SVN working copy |

## Sources

- Direct examination of `~/svn/gxmldoc/docs/` (1,716 RST files, conf.py, GAUSSDomain.py, GAUSSRoles.py)
- RST/docutils parsing behavior: HIGH confidence (stable, well-documented API)
- Sphinx 9.x API stability: MEDIUM confidence (could not verify recent changes without WebSearch)
- Auto-fix corruption risks: HIGH confidence (well-known issue in documentation tooling)
- AI review noise patterns: MEDIUM confidence (based on LLM deployment patterns in training data)

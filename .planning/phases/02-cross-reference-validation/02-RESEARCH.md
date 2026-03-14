# Phase 2: Cross-Reference Validation - Research

**Researched:** 2026-03-14
**Domain:** Sphinx environment loading, cross-reference resolution, toctree analysis, function coverage
**Confidence:** HIGH

## Summary

Phase 2 adds Sphinx-aware validation to the existing docutils-based structural checkers from Phase 1. The central challenge is loading the Sphinx build environment with the custom GAUSS domain so that cross-references (`:func:`, `:doc:`, bare backtick refs via `default_role='any'`) resolve through the actual domain resolution pipeline. This is well-supported by Sphinx's Python API -- the `dummy` builder performs a full read phase (parsing all RST, building the domain object registry, constructing the toctree graph) without writing any output files.

The GAUSS domain (`GAUSSDomain.py`) stores all registered functions in `env.domaindata['gauss']['objects']` as a `{fullname: (docname, objtype)}` dict. Cross-reference resolution uses case-insensitive matching (`_search_objects` with `casefold()`). The toctree graph is available via `env.toctree_includes` (parent->children) and orphan detection can leverage `env.files_to_rebuild` plus `env.metadata` (for `:orphan:` markers). Function coverage and See Also validation can be built entirely from the parsed doc data and domain object registry without additional Sphinx features.

**Primary recommendation:** Use `sphinx.application.Sphinx` with `buildername='dummy'` to load the full environment. Extract the GAUSS domain object registry, toctree includes, and metadata. Build four checkers: broken cross-references, orphan pages, function coverage, and See Also validation.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUN-02 | Sphinx environment loads with custom GAUSS domain for cross-reference resolution | Sphinx `dummy` builder loads the full environment including custom domain from conf.py `setup()`. Domain data accessible at `env.domaindata['gauss']['objects']`. Verified GAUSS domain registers via `GAUSSDomain.setup(app)` in conf.py. |
| STRC-03 | Broken cross-reference detection -- all :func:, :doc:, :ref: links resolve through GAUSS domain | Sphinx build produces warnings for unresolved references. Capture via `sphinx.util.logging` or post-build analysis of `env.domaindata['gauss']['objects']` for `:func:` refs, `env.all_docs` for `:doc:` refs. Also handle bare backtick refs (`default_role='any'`). |
| STRC-04 | Orphan page detection -- RST files not in any toctree (respecting :orphan: and include fragments) | `env.files_to_rebuild` tracks docs in toctrees. `env.metadata[docname]` contains `:orphan:` markers. `env.included` tracks `.. include::` fragments. Sphinx's own `check_consistency()` does exactly this check. |
| STRC-07 | Function coverage -- every Command Reference function name appears in at least one code example | `env.domaindata['gauss']['objects']` provides the complete function registry. Phase 1 `ParsedDoc.code_blocks` provides code block content. Cross-reference: check if each function name appears in any `literal_block` content across the corpus. |
| STRC-08 | See Also validation -- seealso links point to existing function pages | See Also sections use `.. seealso::` directive with `:func:` and `:doc:` roles. Parse targets from seealso nodes and validate against domain object registry and `env.all_docs`. |
</phase_requirements>

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sphinx | 9.1.0 | Build environment with GAUSS domain, cross-reference resolution, toctree graph | The docs use Sphinx with a custom GAUSS domain. Only Sphinx's own environment can resolve references through this domain correctly. `dummy` builder does read-phase only (no output files). |
| docutils | 0.22.4 | Already installed from Phase 1 | Sphinx depends on it; used for per-file parsing in fast-mode checkers |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sphinx_design | (existing) | Required by conf.py (grid directives) | Must be installed for Sphinx build to succeed |
| pydata_sphinx_theme | (existing) | Required by conf.py (html_theme) | Must be installed for Sphinx build to succeed |
| pygments | (existing) | Required for GAUSSLexer registration | Must be installed for Sphinx build to succeed |

**Installation:**
```bash
pip install sphinx==9.1.0 sphinx-design pydata-sphinx-theme
```

**Note:** `pyproject.toml` must add `sphinx>=9.0` to dependencies.

## Architecture Patterns

### Sphinx Environment Loader (`parser/sphinx_env.py`)

Central new component. Loads Sphinx with the dummy builder, provides access to domain data.

```python
from sphinx.application import Sphinx
from pathlib import Path
import tempfile

def load_sphinx_env(docs_dir: str) -> "BuildEnvironment":
    """Load Sphinx environment with GAUSS domain using dummy builder."""
    srcdir = str(Path(docs_dir).resolve())
    outdir = tempfile.mkdtemp(prefix="gauss-qa-build-")
    doctreedir = tempfile.mkdtemp(prefix="gauss-qa-doctrees-")

    app = Sphinx(
        srcdir=srcdir,
        confdir=srcdir,       # conf.py is in docs dir
        outdir=outdir,
        doctreedir=doctreedir,
        buildername="dummy",  # read phase only, no output
        freshenv=True,        # clean build each time
    )
    app.build()
    return app.env
```

**Key data available after build:**
- `env.domaindata['gauss']['objects']` -- `{fullname: (docname, objtype)}` for all registered functions
- `env.domaindata['gauss']['modules']` -- module registry
- `env.all_docs` -- `{docname: mtime}` for all processed documents
- `env.toctree_includes` -- `{docname: [child_docnames]}` toctree parent-child map
- `env.files_to_rebuild` -- `{docname: set_of_parent_docs}` (docs included in some toctree)
- `env.metadata` -- `{docname: dict}` including `:orphan:` markers
- `env.included` -- `{docname: set_of_included_files}` for `.. include::` directives

### Checker Architecture

Phase 2 adds four new checkers, all with `requires_sphinx = True`:

```
checkers/
    links.py          # STRC-03: broken :func:, :doc:, :ref:, bare backtick refs
    orphans.py        # STRC-04: pages not in any toctree
    coverage.py       # STRC-07: function names in code examples
    seealso.py        # STRC-08: seealso targets exist
```

All Sphinx-mode checkers receive the `BuildEnvironment` via `**kwargs`:
```python
class LinksChecker(BaseChecker):
    name = "links"
    requires_sphinx = True

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        env = kwargs["sphinx_env"]
        # ... validate cross-refs against env
```

### CLI Extension

Add a `check-refs` subcommand (or extend `scan` with `--sphinx` flag) that:
1. Loads the Sphinx environment (30-60 seconds)
2. Runs all `requires_sphinx=True` checkers
3. Produces findings through the same report pipeline

```bash
gauss-qa --docs-dir ~/svn/gxmldoc/docs check-refs           # all cross-ref checks
gauss-qa --docs-dir ~/svn/gxmldoc/docs check-refs --check links  # just broken links
gauss-qa --docs-dir ~/svn/gxmldoc/docs scan --sphinx         # all checks (fast + sphinx)
```

### Recommended Project Structure (additions to existing)

```
src/gauss_doc_qa/
    parser/
        sphinx_env.py      # NEW: Sphinx environment loader
    checkers/
        links.py           # NEW: broken cross-reference detection
        orphans.py         # NEW: orphan page detection
        coverage.py        # NEW: function coverage in code examples
        seealso.py         # NEW: See Also link validation
```

### Data Flow for Cross-Reference Validation

```
1. Load Sphinx env (dummy builder) -> BuildEnvironment
2. Extract domain data:
   - gauss_objects = env.domaindata['gauss']['objects']
   - all_docs = set(env.all_docs.keys())
3. For each RST file:
   a. Parse with docutils (existing Phase 1 parser)
   b. Extract cross-references from parsed AST:
      - pending_xref nodes (Sphinx) or reference/problematic nodes (docutils)
      - :func:`target` -> check target in gauss_objects
      - :doc:`target` -> check target in all_docs
      - bare `target` -> check via resolve_any_xref logic
   c. Extract seealso targets -> validate against registries
4. Build toctree graph from env.toctree_includes
5. Walk graph from root_doc to find unreachable pages
6. Cross-check function names against code block content corpus
```

### Important: Sphinx Warning Capture Strategy

**Option A (recommended): Post-build analysis.** After the dummy build completes, analyze the environment data directly. Check each cross-reference target against the registries. This gives full control over finding format and doesn't depend on Sphinx's warning format.

**Option B: Warning interception.** Hook into Sphinx's `missing-reference` event during build to capture unresolved refs. More integrated but couples us to Sphinx's internal event system.

Use Option A. It is simpler, more testable, and produces findings in our format without parsing Sphinx warning strings.

### Cross-Reference Extraction from docutils AST

Since Phase 1 parses with docutils (not Sphinx), Sphinx-specific nodes like `pending_xref` are not created. Instead, docutils produces:
- **`reference` nodes** for explicit `:doc:` and external links
- **`problematic` nodes** for unrecognized roles (`:func:` becomes problematic text in docutils)
- **`system_message` nodes** warning about unknown roles

For Phase 2 cross-reference extraction, use regex on raw RST content to extract role references, then validate against the Sphinx environment:

```python
import re
XREF_RE = re.compile(r':(\w+):`([^`]+)`')     # :role:`target`
BARE_REF_RE = re.compile(r'(?<!:)`([^`]+)`(?!`)') # bare backtick refs
```

This is acceptable because we are not parsing RST structure -- we are extracting reference targets for validation against the already-built Sphinx environment. The structure has been validated by the Sphinx build itself.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-reference resolution | Custom `:func:` target resolver | Sphinx `dummy` build + `env.domaindata['gauss']['objects']` | The GAUSS domain has case-insensitive matching, module-scoped resolution, and `default_role='any'` semantics. Reimplementing this is error-prone. |
| Toctree graph traversal | Custom RST toctree parser | `env.toctree_includes` from Sphinx build | Sphinx handles glob patterns, hidden toctrees, numbered toctrees, and `:orphan:` metadata. |
| `:orphan:` directive handling | Custom metadata parser | `env.metadata[docname]` | Sphinx already extracts file-level metadata directives during the read phase. |
| Include fragment tracking | Custom `.. include::` scanner | `env.included` | Sphinx tracks which files are included from which documents. |
| Domain object registry | Custom function name extraction from RST | `env.domaindata['gauss']['objects']` | Domain already builds complete registry during build. |

**Key insight:** The Sphinx dummy build already does all the hard work. Our job is to extract data from the build environment and format it as `Finding` objects.

## Common Pitfalls

### Pitfall 1: Sphinx Build Failure Due to Missing Dependencies

**What goes wrong:** The GAUSS docs conf.py imports `GAUSSLexer`, `GAUSSDomain`, `GAUSSRoles`, and `GAUSSHTMLTranslator` from `docs/util/`. It also requires `sphinx_design` and `pydata_sphinx_theme`. If any are missing, the Sphinx build fails before producing an environment.

**Why it happens:** The conf.py `setup()` function does `sys.path.insert(0, ...)` to find the util modules, but the installed Python environment may lack `sphinx_design` or `pydata_sphinx_theme`.

**How to avoid:** Install all required dependencies. Test the Sphinx environment loading against the actual docs directory early. The `dummy` builder still requires the theme to be installed (Sphinx validates theme existence during app init even for non-HTML builders -- verify this and if dummy avoids it, simplify).

**Warning signs:** `ModuleNotFoundError` or `ThemeError` during `app = Sphinx(...)`.

### Pitfall 2: Case Sensitivity in Function Name Matching

**What goes wrong:** GAUSS function names are case-insensitive. The domain's `_search_objects` uses `casefold()` for matching. If our coverage checker does case-sensitive string matching against code blocks, it will miss functions written in different case.

**How to avoid:** Always use `casefold()` or `.lower()` when matching function names against code block content.

### Pitfall 3: Bare Backtick References (default_role='any')

**What goes wrong:** With `default_role = 'any'`, bare backtick text like `` `trap` `` or `` `by` `` goes through `resolve_any_xref()`. Some of these are intentional references to keywords/functions, others are just inline code styling. Flagging all unresolved bare refs as broken links produces noise.

**How to avoid:** Classify bare backtick references separately from explicit `:func:` references. Report unresolved `:func:` refs as ERROR, unresolved bare backtick refs as INFO or WARNING (lower severity). Consider a known-keywords allowlist for common GAUSS keywords (`trap`, `by`, `call`, etc.) that are not in the domain registry but are valid language constructs.

### Pitfall 4: Orphan False Positives on Include Fragments

**What goes wrong:** Files in `include/` directory (e.g., `plotattrremark.rst`) are not standalone pages and are never in any toctree. A naive orphan checker flags them.

**How to avoid:** Check both `env.included` (for `.. include::` fragments) and the `DocType.INCLUDE_FRAGMENT` classification from Phase 1. Exclude these from orphan checking entirely.

### Pitfall 5: Confusing exclude_patterns with Orphans

**What goes wrong:** conf.py has `exclude_patterns` that prevent certain RST files from being processed by Sphinx at all. These files won't appear in `env.all_docs` and should not be flagged as orphans or checked for cross-references.

**How to avoid:** Respect `env.all_docs` as the source of truth for which documents were processed. Files excluded by Sphinx configuration are outside scope.

### Pitfall 6: Sphinx Build Time Blocking the CLI

**What goes wrong:** The dummy build takes 30-60 seconds on 1,700 files. Users running `scan` for quick structural checks get blocked by Sphinx loading.

**How to avoid:** Keep Sphinx-mode checks in a separate CLI subcommand (`check-refs`) or behind a `--sphinx` flag. Fast docutils-only checks remain available without waiting for the Sphinx build.

### Pitfall 7: Function Coverage False Positives from Utility Functions

**What goes wrong:** Some Command Reference functions are documented but rarely used in examples outside their own page. Flagging every function that lacks a code example elsewhere is noisy for utility functions like `close`, `end`, `cls`.

**How to avoid:** For STRC-07, check if the function name appears in **any** code example in the entire corpus (including its own page). The requirement says "appears in at least one code example somewhere in the docs." The function's own page examples count.

## Code Examples

### Loading Sphinx Environment

```python
# Source: Sphinx 9.1.0 API, verified via official docs
from sphinx.application import Sphinx
import tempfile

def load_sphinx_env(docs_dir: str):
    """Load Sphinx environment with GAUSS domain."""
    outdir = tempfile.mkdtemp(prefix="gauss-qa-")
    doctreedir = tempfile.mkdtemp(prefix="gauss-qa-dt-")

    app = Sphinx(
        srcdir=docs_dir,
        confdir=docs_dir,
        outdir=outdir,
        doctreedir=doctreedir,
        buildername="dummy",
        freshenv=True,
    )
    app.build()
    return app.env
```

### Accessing GAUSS Domain Objects

```python
# After loading env:
gauss_objects = env.domaindata['gauss']['objects']
# gauss_objects = {'abs': ('abs', 'function'), 'olsmt': ('olsmt', 'function'), ...}

# Check if a function target resolves:
def func_exists(name: str, objects: dict) -> bool:
    name_lower = name.casefold()
    return any(k.casefold() == name_lower for k in objects)
```

### Extracting Cross-References from Raw RST

```python
import re

ROLE_REF_RE = re.compile(r':(\w+):`~?([^`<]+?)(?:\s*<[^>]+>)?`')
# Matches :func:`abs`, :doc:`getting-started/index`, :func:`~module.func`

def extract_xrefs(rst_content: str) -> list[tuple[str, str, int]]:
    """Extract (role, target, line_number) tuples from RST content."""
    refs = []
    for i, line in enumerate(rst_content.splitlines(), 1):
        for m in ROLE_REF_RE.finditer(line):
            role = m.group(1)
            target = m.group(2).lstrip('~').lstrip('.')
            refs.append((role, target, i))
    return refs
```

### Orphan Detection Logic

```python
def find_orphans(env) -> list[str]:
    """Find documents not reachable from root via toctree."""
    root = env.config.root_doc  # 'index'
    reachable = set()
    _walk_toctree(root, env.toctree_includes, reachable)

    included_fragments = set()
    for doc_includes in env.included.values():
        included_fragments.update(doc_includes)

    orphans = []
    for docname in env.all_docs:
        if docname in reachable:
            continue
        if docname in included_fragments:
            continue
        if 'orphan' in env.metadata.get(docname, {}):
            continue
        orphans.append(docname)
    return orphans

def _walk_toctree(docname, toctree_includes, visited):
    if docname in visited:
        return
    visited.add(docname)
    for child in toctree_includes.get(docname, []):
        _walk_toctree(child, toctree_includes, visited)
```

### See Also Extraction from RST

```python
# See Also sections use the pattern:
# .. seealso:: Functions :func:`glm`, :func:`gmmFitIV`, ...
# .. seealso:: Operators :doc:`subtraction`, :doc:`element-by-element-multiplication`

SEEALSO_RE = re.compile(r'\.\.\s+seealso::\s*(.*)', re.MULTILINE)

def extract_seealso_targets(rst_content: str) -> list[tuple[str, str, int]]:
    """Extract (role, target, line_number) from seealso directives."""
    refs = []
    for i, line in enumerate(rst_content.splitlines(), 1):
        m = SEEALSO_RE.match(line.strip())
        if m:
            content = m.group(1)
            for ref_match in ROLE_REF_RE.finditer(content):
                refs.append((ref_match.group(1), ref_match.group(2), i))
    return refs
```

### Function Coverage Check

```python
def check_function_coverage(
    gauss_objects: dict,
    all_code_blocks: dict[str, list[str]],  # docname -> list of code block contents
    command_ref_docs: set[str],
) -> list[str]:
    """Find functions with no code example mention anywhere in docs."""
    # Build corpus of all code block text (case-folded)
    all_code_text = ""
    for blocks in all_code_blocks.values():
        all_code_text += "\n".join(blocks).casefold() + "\n"

    uncovered = []
    for funcname, (docname, objtype) in gauss_objects.items():
        if objtype != 'function':
            continue
        if docname not in command_ref_docs:
            continue
        # Check if function name appears in any code block
        if funcname.casefold() not in all_code_text:
            uncovered.append(funcname)
    return uncovered
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Shell out to `sphinx-build` and parse warnings | Use `sphinx.application.Sphinx` Python API | Sphinx 1.0+ (stable) | Programmatic access to env, no warning string parsing |
| `sphinx-build -b linkcheck` | Domain object registry analysis | N/A | linkcheck only validates external URLs, not internal cross-refs |
| Manual cross-ref tracking | `env.domaindata` with full domain resolution | Built into Sphinx | Complete, accurate reference resolution |

**Sphinx 9.x notes:**
- The `dummy` builder is available and stable (introduced in Sphinx 2.x, still present in 9.1.0)
- `BuildEnvironment` API is stable across major versions for the attributes we need
- Sphinx 9.x changed some internal APIs but `app.build()`, `app.env`, `env.domaindata`, `env.toctree_includes`, `env.all_docs`, `env.metadata`, `env.included` remain stable
- The `freshenv=True` parameter ensures clean builds without stale cached data

## Open Questions

1. **Does the `dummy` builder require theme installation?**
   - What we know: conf.py sets `html_theme = 'pydata_sphinx_theme'`. The dummy builder skips HTML output.
   - What's unclear: Whether Sphinx validates theme existence during initialization regardless of builder.
   - Recommendation: Test early. If theme is required, install it. If not, document that dummy builder bypasses theme validation.

2. **Sphinx build performance on 1,700 files**
   - What we know: Research estimates 30-60 seconds. This is a one-time cost per run.
   - What's unclear: Actual performance on this specific corpus with the GAUSS domain.
   - Recommendation: Measure during implementation. If >60 seconds, consider caching the environment pickle (OPTM-02 from v2 requirements).

3. **Bare backtick reference severity**
   - What we know: `default_role='any'` means bare backtick text resolves through `resolve_any_xref`. Many bare backtick uses are styling, not cross-references.
   - What's unclear: How many bare backtick references actually resolve vs fail. Whether users want these flagged.
   - Recommendation: Start with INFO severity for unresolved bare refs. Provide a `--strict` flag to elevate to WARNING.

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest >= 8.0 |
| Config file | None (default pytest discovery) |
| Quick run command | `pytest gauss-doc-qa/tests/ -x -q` |
| Full suite command | `pytest gauss-doc-qa/tests/ -v` |

### Phase Requirements to Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUN-02 | Sphinx env loads with GAUSS domain, domain data accessible | integration | `pytest gauss-doc-qa/tests/test_sphinx_env.py -x` | No -- Wave 0 |
| STRC-03 | Broken :func:, :doc: links detected; valid links pass | unit | `pytest gauss-doc-qa/tests/test_links.py -x` | No -- Wave 0 |
| STRC-04 | Orphan pages detected; :orphan: pages excluded; include fragments excluded | unit | `pytest gauss-doc-qa/tests/test_orphans.py -x` | No -- Wave 0 |
| STRC-07 | Functions without code examples flagged; functions with examples pass | unit | `pytest gauss-doc-qa/tests/test_coverage.py -x` | No -- Wave 0 |
| STRC-08 | Seealso refs to non-existent functions/pages flagged | unit | `pytest gauss-doc-qa/tests/test_seealso.py -x` | No -- Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest gauss-doc-qa/tests/ -x -q`
- **Per wave merge:** `pytest gauss-doc-qa/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps

- [ ] `gauss-doc-qa/tests/test_sphinx_env.py` -- covers FOUN-02 (Sphinx env loading, can be tested with a minimal conf.py fixture or mocked)
- [ ] `gauss-doc-qa/tests/test_links.py` -- covers STRC-03
- [ ] `gauss-doc-qa/tests/test_orphans.py` -- covers STRC-04
- [ ] `gauss-doc-qa/tests/test_coverage.py` -- covers STRC-07
- [ ] `gauss-doc-qa/tests/test_seealso.py` -- covers STRC-08
- [ ] `gauss-doc-qa/tests/fixtures/` -- minimal RST fixtures for cross-ref testing (mock Sphinx env data or use tiny Sphinx project)

**Testing strategy note:** Unit tests for checkers should mock the Sphinx environment data (provide dicts/sets directly) rather than running actual Sphinx builds. Integration tests for the Sphinx loader should use a minimal test docs directory with a few RST files and a simple conf.py, not the full 1,700-file corpus.

## Sources

### Primary (HIGH confidence)
- `~/svn/gxmldoc/docs/util/GAUSSDomain.py` -- inspected. Custom domain with `name='gauss'`, case-insensitive `find_obj()`, `resolve_xref()`, `resolve_any_xref()`. Objects stored in `env.domaindata['gauss']['objects']`.
- `~/svn/gxmldoc/docs/util/GAUSSRoles.py` -- inspected. Only registers `menuselection` role. Minimal impact.
- `~/svn/gxmldoc/docs/conf.py` -- inspected. `primary_domain='gauss'`, `default_role='any'`, `exclude_patterns` for dbnomics/fred files, extensions include `sphinx_design`.
- `~/svn/gxmldoc/docs/util/GAUSSHTMLTranslator.py` -- inspected. Custom nodes `desc_returnlist`, `desc_return` registered by GAUSSDomain.setup().
- [Sphinx Builders docs](https://www.sphinx-doc.org/en/master/usage/builders/index.html) -- verified `dummy` builder: "produces no output, input is only parsed and checked for consistency."
- [Sphinx Domain API](https://www.sphinx-doc.org/en/master/extdev/domainapi.html) -- verified `get_objects()`, `resolve_xref()`, domain data storage in `env.domaindata`.
- [Sphinx BuildEnvironment source](https://www.sphinx-doc.org/en/master/_modules/sphinx/environment.html) -- verified `check_consistency()`, `toctree_includes`, `included`, `metadata`, `all_docs`, `files_to_rebuild` attributes.

### Secondary (MEDIUM confidence)
- Sphinx 9.1.0 API stability -- `app.build()`, `app.env`, `env.domaindata` patterns are stable across Sphinx 7.x-9.x based on source review and documentation. MEDIUM because could not execute a test build to verify.

### Tertiary (LOW confidence)
- `pydata_sphinx_theme` requirement for dummy builder -- unclear if dummy builder validates theme. Needs testing.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Sphinx dummy builder and domain API are well-documented and stable
- Architecture: HIGH -- Pattern follows Sphinx's own internal design for consistency checking
- Pitfalls: HIGH -- Based on direct inspection of GAUSSDomain.py, conf.py, and real RST files
- Cross-reference patterns: HIGH -- Verified by examining actual `:func:`, `:doc:`, seealso, and bare backtick usage in the corpus

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (Sphinx API is stable; 30 days appropriate)

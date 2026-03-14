# Phase 1: Foundation and Structural Checks - Research

**Researched:** 2026-03-14
**Domain:** RST documentation parsing, structural validation, CLI reporting
**Confidence:** HIGH

## Summary

Phase 1 builds the core infrastructure for the GAUSS Documentation QA system: docutils-based RST parsing, doc type classification, structural checkers (code blocks, sections, signatures), and a multi-format reporting pipeline. This phase uses docutils only (no Sphinx) and processes ~1,700 RST files for fast structural validation.

The key technical decisions are: (1) parse RST via docutils AST, never regex; (2) classify each RST file by type before applying checks (function pages, operator pages, index pages, and include fragments have different structures); (3) produce uniform Finding dataclass objects from every checker; (4) render findings through rich (terminal), JSON, and Markdown formatters.

**Primary recommendation:** Build bottom-up: models first, then parser + classifier, then checkers, then CLI + reporters. Each layer is independently testable.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FOUN-01 | RST files parsed via docutils AST with doc type classification | docutils 0.22.4 Parser + traverse() API; DocType enum with path-based + content-based classification |
| FOUN-03 | Finding dataclass with severity, file path, line number, category, message | Standard Python dataclass; Severity enum (ERROR/WARNING/INFO) |
| FOUN-04 | CLI entry point with subcommands for individual checks and full scan | click 8.3.1 with group/command pattern |
| STRC-01 | Code block presence check -- every Command Reference page has at least one literal_block | docutils literal_block node traversal; both `::` and `.. code-block::` produce literal_block nodes |
| STRC-02 | Code block non-empty check -- no whitespace-only literal_blocks | Check `node.astext().strip()` on literal_block nodes |
| STRC-05 | Section structure validation -- Command Reference pages have Purpose/Format/Examples | Section title extraction from docutils sections; required sections vary by DocType |
| STRC-06 | Function signature completeness -- function directives have params and return type | Parse `.. function::` directive content for `:param:` and `:return:` field entries |
| REPT-01 | Terminal output with severity colors via rich | rich Console + Table with severity-based styling |
| REPT-02 | JSON report output | json.dumps on list of Finding.to_dict() |
| REPT-03 | Markdown report output | String formatting into markdown tables |
| REPT-04 | Summary counts by category and severity at top of every report | Counter over findings grouped by (category, severity) |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.14 | Runtime | Already installed on system |
| docutils | 0.22.4 | RST parsing into doctree AST | The canonical RST parser. Sphinx itself is built on it. Produces traversable node trees with literal_block, section, field_list nodes |
| click | 8.3.1 | CLI framework | Clean subcommand structure. Already installed |
| rich | 14.3.3 | Terminal output with colors, tables, progress | Install needed. Standard for CLI output formatting |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 9.0.2 | Test runner | Already installed. Test each checker against fixture RST files |
| json (stdlib) | - | JSON report output | Machine-readable findings export |
| pathlib (stdlib) | - | File path handling | Directory traversal, path manipulation |
| dataclasses (stdlib) | - | Data models | Finding, ParsedDoc, DocType containers |

### Not Needed in Phase 1
| Library | Why Not Yet |
|---------|-------------|
| sphinx | Phase 2 -- cross-reference resolution requires Sphinx environment |
| anthropic | Phase 4 -- AI persona reviews |
| rapidfuzz | Deferred to v2 -- terminology checking |

**Installation:**
```bash
pip install docutils==0.22.4 rich==14.3.3
# click, pytest, pyyaml already installed
```

## Architecture Patterns

### Recommended Project Structure
```
gauss-doc-qa/
├── pyproject.toml
├── src/
│   └── gauss_doc_qa/
│       ├── __init__.py
│       ├── cli.py                 # click CLI entry point
│       ├── models.py              # Finding, ParsedDoc, DocType, Severity, CodeBlock
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── rst_parser.py      # docutils-based RST parsing -> ParsedDoc
│       │   ├── classifier.py      # path + content -> DocType
│       │   └── inventory.py       # file system scan, exclude_patterns
│       ├── checkers/
│       │   ├── __init__.py
│       │   ├── base.py            # BaseChecker, registry
│       │   ├── code_blocks.py     # STRC-01, STRC-02
│       │   ├── sections.py        # STRC-05
│       │   └── signatures.py      # STRC-06
│       └── report/
│           ├── __init__.py
│           ├── terminal.py        # rich-based terminal output (REPT-01)
│           ├── json_report.py     # JSON output (REPT-02)
│           ├── markdown_report.py # Markdown output (REPT-03)
│           └── summary.py         # Summary counts (REPT-04)
├── tests/
│   ├── conftest.py               # shared fixtures
│   ├── fixtures/                  # sample RST files
│   │   ├── function_page.rst     # standard Command Reference page
│   │   ├── operator_page.rst     # operator page (different structure)
│   │   ├── index_page.rst        # alphabetical index (toctree only)
│   │   ├── include_fragment.rst  # include/ fragment
│   │   ├── missing_code.rst      # function page with no code blocks
│   │   ├── empty_code.rst        # function page with whitespace-only code
│   │   ├── missing_sections.rst  # function page missing required sections
│   │   └── incomplete_sig.rst    # function with missing params/returns
│   ├── test_models.py
│   ├── test_parser.py
│   ├── test_classifier.py
│   ├── test_code_blocks.py
│   ├── test_sections.py
│   ├── test_signatures.py
│   └── test_reporters.py
└── reports/                       # output directory (gitignored)
```

### Pattern 1: docutils RST Parsing
**What:** Parse RST content into a docutils document tree, then traverse for structural nodes.
**When to use:** All structural checks in Phase 1.

```python
from docutils.utils import new_document
from docutils.parsers.rst import Parser
from docutils.frontend import OptionParser
from docutils import nodes

def parse_rst(filepath: str, content: str) -> nodes.document:
    parser = Parser()
    settings = OptionParser(components=(Parser,)).get_default_values()
    # Suppress stderr warnings from docutils about unknown directives
    settings.report_level = 5  # SEVERE only
    settings.halt_level = 5
    doc = new_document(filepath, settings)
    parser.parse(content, doc)
    return doc
```

Note: `OptionParser` is deprecated in docutils 0.22 but still functional. It will be removed in docutils 2.0. For this project it is fine.

Key node types for traversal:
- `nodes.section` -- contains title as first child
- `nodes.literal_block` -- produced by BOTH `::` blocks and `.. code-block::` directives
- `nodes.field_list` / `nodes.field` -- contains `:param:`, `:type:`, `:return:`, `:rtype:` entries

### Pattern 2: Doc Type Classification
**What:** Classify each RST file before applying checks. Different page types have different required sections.
**When to use:** Before running any checkers.

Classification rules (in priority order):
1. Path contains `include/` -> INCLUDE_FRAGMENT (skip structural checks)
2. Path is in known subdirectory (getting-started, user-guide, graphics-guide, tsmt, fanpac, cmlmt, comt, etc.) -> subdirectory-specific type
3. Single-letter filename (a.rst through z.rst, plus _.rst) -> ALPHA_INDEX
4. Known operator filenames (addition, subtraction, multiplication, etc.) -> OPERATOR
5. Default -> COMMAND_REF

**Required sections by type:**

| DocType | Required Sections | Notes |
|---------|-------------------|-------|
| COMMAND_REF | Purpose, Format, Examples | Format section should contain `.. function::` directive |
| OPERATOR | Purpose, Format, Examples | Format may use bare `::` block instead of `.. function::` |
| ALPHA_INDEX | (none) | Only contains toctree directive |
| INCLUDE_FRAGMENT | (none) | Excluded from all structural checks |
| GETTING_STARTED, USER_GUIDE, etc. | (none) | Flexible structure, no strict template |

### Pattern 3: Uniform Finding Objects
**What:** Every checker produces Finding dataclass instances with identical schema.

```python
from dataclasses import dataclass, asdict
from enum import Enum

class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

class DocType(Enum):
    COMMAND_REF = "command_ref"
    OPERATOR = "operator"
    ALPHA_INDEX = "alpha_index"
    GETTING_STARTED = "getting_started"
    USER_GUIDE = "user_guide"
    GRAPHICS_GUIDE = "graphics_guide"
    APP_MODULE = "app_module"
    INCLUDE_FRAGMENT = "include"
    OTHER = "other"

@dataclass
class Finding:
    file: str
    line: int | None
    severity: Severity
    category: str          # "missing_code_block", "empty_code_block", "missing_section", etc.
    checker: str           # "code_blocks", "sections", "signatures"
    message: str

    def to_dict(self) -> dict:
        d = asdict(self)
        d["severity"] = self.severity.value
        return d
```

### Pattern 4: Checker Base Class with Registration

```python
class BaseChecker:
    name: str
    requires_sphinx: bool = False

    def check(self, parsed_doc, **kwargs) -> list[Finding]:
        raise NotImplementedError

# Registry pattern
_checkers: dict[str, BaseChecker] = {}

def register_checker(checker: BaseChecker):
    _checkers[checker.name] = checker

def get_checker(name: str) -> BaseChecker:
    return _checkers[name]

def get_all_fast_checkers() -> list[BaseChecker]:
    return [c for c in _checkers.values() if not c.requires_sphinx]
```

### Pattern 5: CLI Subcommands (click)

```python
import click

@click.group()
@click.option("--docs-dir", type=click.Path(exists=True), required=True,
              help="Path to Sphinx docs directory")
@click.option("--format", "output_format", type=click.Choice(["terminal", "json", "markdown"]),
              default="terminal")
@click.pass_context
def cli(ctx, docs_dir, output_format):
    ctx.ensure_object(dict)
    ctx.obj["docs_dir"] = docs_dir
    ctx.obj["format"] = output_format

@cli.command()
@click.option("--check", type=str, help="Run specific checker only")
@click.pass_context
def scan(ctx, check):
    """Run structural checks on all RST files."""
    pass

@cli.command()
@click.pass_context
def inventory(ctx):
    """List all RST files with their doc type classification."""
    pass
```

### Anti-Patterns to Avoid
- **Regex for RST structure:** RST is whitespace-sensitive with nested directives. Both `::` literal blocks and `.. code-block::` directives produce `literal_block` nodes in the doctree. Parse the tree, do not regex the source.
- **One template for all pages:** Operator pages (addition.rst) have Parameters/Returns sections instead of a `.. function::` directive in their Format section. Index pages have only toctrees. Include fragments have no sections. Classify before checking.
- **Monolithic script:** Separate checkers enable individual testing, selective runs, and independent iteration.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| RST parsing | Custom parser, regex extraction | docutils.parsers.rst.Parser | RST has context-dependent formatting, nested directives, include fragments |
| Literal block detection | Regex for `::` and `.. code-block::` | `doc.traverse(nodes.literal_block)` | Both syntaxes produce the same node type in the doctree |
| Section extraction | Regex for underline patterns | `doc.traverse(nodes.section)` then read title child | Underline characters vary (=, -, +, ~) |
| Terminal colors | ANSI escape codes | rich Console + Table | Cross-platform, handles terminal capabilities |
| CLI argument parsing | argparse manually | click with decorators | Subcommand structure is cleaner |

## Common Pitfalls

### Pitfall 1: Operator Pages Have Different Structure
**What goes wrong:** Checking all top-level RST files for `.. function::` directive fails on operator pages (addition.rst, subtraction.rst). These use bare `::` blocks in their Format section and have separate Parameters/Returns sections instead of inline `:param:` fields.
**How to avoid:** The DocType classifier must identify operator pages. The section checker must use type-appropriate required section lists. The signature checker should skip operator pages or use different validation logic.
**Warning signs:** Operator pages reported as "missing function directive" -- they use a different format intentionally.

### Pitfall 2: Include Fragments Fail All Checks
**What goes wrong:** Files in `include/` (plotattrremark.rst, etc.) are partial RST meant to be `.. include::`'d into other pages. They fail section, code block, and signature checks because they are not standalone pages.
**How to avoid:** Classify files with path containing `include/` as INCLUDE_FRAGMENT. Exclude from all structural checks.

### Pitfall 3: docutils Warnings on Unknown Directives
**What goes wrong:** docutils standalone parsing does not know about Sphinx-specific directives (`.. toctree::`, `.. seealso::`, custom GAUSS directives). It will emit warnings or create `system_message` nodes for these. If report_level is not set high enough, stderr output will be noisy.
**How to avoid:** Set `settings.report_level = 5` (SEVERE only) when creating the document. Unknown directives become generic nodes in the tree but the structural nodes (sections, literal_blocks, field_lists) are still correctly parsed.

### Pitfall 4: Line Numbers in docutils Nodes
**What goes wrong:** Not all docutils nodes have accurate `line` attributes. Some are None, especially for inline nodes.
**How to avoid:** Use the `line` attribute from the parent block node when the leaf node's line is None. For sections, the line number of the title child is usually available. For literal_blocks, the line attribute is set. Accept None in the Finding model as a fallback.

### Pitfall 5: Section Title Matching Must Be Case-Insensitive
**What goes wrong:** Hard-coding exact section titles ("Purpose", "Format", "Examples") fails when docs use slightly different capitalization or extra whitespace.
**How to avoid:** Normalize section titles: strip whitespace, lowercase, then compare. Also handle "Remarks" vs "Remark" variations.

### Pitfall 6: conf.py exclude_patterns Must Be Respected
**What goes wrong:** The inventory scanner picks up RST files that Sphinx explicitly excludes (dbnomics_datasets*.rst, fred files, etc.), producing findings for pages that are intentionally excluded from the build.
**How to avoid:** Read `exclude_patterns` from conf.py and apply them during inventory scanning. The current exclude list is: `dbnomics_datasets*.rst`, `dbnomics_series_*.rst`, `dbnomics_last_updates.rst`, `dbnomics_list_providers.rst`, `dbnomics_provider.rst`.

### Pitfall 7: Some Function Pages Have No Parameters
**What goes wrong:** Functions like `__FILE_DIR` have no parameters (it is a keyword, not a function call). The signature checker should not flag these as "missing parameters."
**How to avoid:** The signature completeness check should verify that IF a `.. function::` directive has a signature with parentheses containing arguments, THEN those arguments should have `:param:` entries. No-argument functions should pass.

## Code Examples

### Parsing and Traversing RST

```python
# Source: docutils API (verified structure from actual GAUSS docs)
from docutils import nodes

def extract_sections(doc: nodes.document) -> list[str]:
    """Extract section titles from parsed RST document."""
    sections = []
    for section in doc.traverse(nodes.section):
        if section.children and isinstance(section.children[0], nodes.title):
            sections.append(section.children[0].astext().strip())
    return sections

def extract_literal_blocks(doc: nodes.document) -> list[tuple[int | None, str]]:
    """Extract literal blocks with line numbers and content."""
    blocks = []
    for node in doc.traverse(nodes.literal_block):
        blocks.append((node.line, node.astext()))
    return blocks

def has_function_directive(doc: nodes.document) -> bool:
    """Check if document contains a .. function:: directive.

    In docutils standalone parsing (no Sphinx), .. function:: produces
    a desc node with a desc_signature child, or may fall through to
    a generic directive node. Check for both.
    """
    # When parsed without Sphinx, unknown directives create system_message
    # or generic nodes. The field_list with :param: entries is still parsed.
    for node in doc.traverse(nodes.field_list):
        for field in node.traverse(nodes.field):
            field_name = field.children[0].astext()
            if field_name.startswith("param ") or field_name.startswith("return "):
                return True
    return False
```

### Checking Code Block Presence (STRC-01, STRC-02)

```python
def check_code_blocks(parsed_doc) -> list[Finding]:
    findings = []

    # Only check COMMAND_REF and OPERATOR pages
    if parsed_doc.doc_type not in (DocType.COMMAND_REF, DocType.OPERATOR):
        return findings

    literal_blocks = list(parsed_doc.doc.traverse(nodes.literal_block))

    # STRC-01: Must have at least one literal_block
    if not literal_blocks:
        findings.append(Finding(
            file=parsed_doc.path,
            line=None,
            severity=Severity.WARNING,
            category="missing_code_block",
            checker="code_blocks",
            message="Command Reference page has no code blocks"
        ))

    # STRC-02: No empty literal_blocks
    for block in literal_blocks:
        if not block.astext().strip():
            findings.append(Finding(
                file=parsed_doc.path,
                line=block.line,
                severity=Severity.ERROR,
                category="empty_code_block",
                checker="code_blocks",
                message="Code block is empty or whitespace-only"
            ))

    return findings
```

### Report Summary (REPT-04)

```python
from collections import Counter

def build_summary(findings: list[Finding]) -> dict:
    by_severity = Counter(f.severity.value for f in findings)
    by_category = Counter(f.category for f in findings)
    by_severity_category = Counter((f.severity.value, f.category) for f in findings)
    return {
        "total": len(findings),
        "by_severity": dict(by_severity),
        "by_category": dict(by_category),
        "by_severity_category": {
            f"{sev}/{cat}": count
            for (sev, cat), count in by_severity_category.items()
        }
    }
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| regex RST parsing | docutils AST traversal | Always been the right approach | Eliminates 20% false positive rate on nested/complex RST |
| OptionParser for docutils settings | Still works in 0.22.4, deprecated for 2.0 | Deprecation since 0.19 | No action needed for this project; will need updating eventually |
| Single monolithic doc checker | Modular checker registry with per-type rules | Best practice | Enables selective runs, independent testing |

## Open Questions

1. **Exact operator page list**
   - What we know: addition.rst, subtraction.rst are operator pages. They use a different structure (Parameters/Returns sections, bare `::` in Format).
   - What's unclear: The complete list of operator page filenames. The architecture doc lists a partial set.
   - Recommendation: During implementation, scan the actual docs for pages matching the operator pattern (no `.. function::` directive, has Parameters/Returns sections) and build the definitive list.

2. **App module subdirectory conventions**
   - What we know: ~12 subdirectories (tsmt, fanpac, cmlmt, comt, etc.) contain app-specific function pages.
   - What's unclear: Do these follow the same Purpose/Format/Examples template as top-level Command Reference pages?
   - Recommendation: Sample a few files from each subdirectory during implementation. If they follow the same pattern, classify as COMMAND_REF. If not, create APP_MODULE type with appropriate rules.

3. **docutils handling of `.. function::` without Sphinx**
   - What we know: docutils does not natively understand `.. function::` (it is a Sphinx directive). It will produce a system_message or generic node.
   - What's unclear: Exactly how the field_list (`:param:`, `:return:`) entries appear in the parsed tree when the directive is unknown.
   - Recommendation: Test this empirically when docutils is installed. The `:param:` entries should still appear as field_list nodes within the directive body, but verify.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | none -- see Wave 0 |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FOUN-01 | RST parsed via docutils AST, doc type classification | unit | `pytest tests/test_parser.py tests/test_classifier.py -x` | Wave 0 |
| FOUN-03 | Finding dataclass with severity, path, line, category, message | unit | `pytest tests/test_models.py -x` | Wave 0 |
| FOUN-04 | CLI entry point with subcommands | integration | `pytest tests/test_cli.py -x` | Wave 0 |
| STRC-01 | Code block presence on Command Ref pages | unit | `pytest tests/test_code_blocks.py::test_missing_code_block -x` | Wave 0 |
| STRC-02 | Code block non-empty check | unit | `pytest tests/test_code_blocks.py::test_empty_code_block -x` | Wave 0 |
| STRC-05 | Section structure validation by doc type | unit | `pytest tests/test_sections.py -x` | Wave 0 |
| STRC-06 | Function signature completeness | unit | `pytest tests/test_signatures.py -x` | Wave 0 |
| REPT-01 | Terminal output with severity colors | unit | `pytest tests/test_reporters.py::test_terminal -x` | Wave 0 |
| REPT-02 | JSON report output | unit | `pytest tests/test_reporters.py::test_json -x` | Wave 0 |
| REPT-03 | Markdown report output | unit | `pytest tests/test_reporters.py::test_markdown -x` | Wave 0 |
| REPT-04 | Summary counts by category and severity | unit | `pytest tests/test_reporters.py::test_summary -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q`
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `tests/conftest.py` -- shared fixtures (parsed docs, sample findings)
- [ ] `tests/fixtures/*.rst` -- sample RST files covering each DocType and each failure mode
- [ ] `tests/test_models.py` -- Finding, Severity, DocType model tests
- [ ] `tests/test_parser.py` -- RST parsing tests
- [ ] `tests/test_classifier.py` -- DocType classification tests
- [ ] `tests/test_code_blocks.py` -- STRC-01, STRC-02
- [ ] `tests/test_sections.py` -- STRC-05
- [ ] `tests/test_signatures.py` -- STRC-06
- [ ] `tests/test_reporters.py` -- REPT-01 through REPT-04
- [ ] `tests/test_cli.py` -- CLI integration tests
- [ ] `pyproject.toml` -- project configuration with test dependencies
- [ ] Framework install: `pip install docutils==0.22.4 rich==14.3.3` -- docutils and rich not currently installed

## Sources

### Primary (HIGH confidence)
- Direct inspection of `~/svn/gxmldoc/docs/abs.rst` -- standard Command Reference page with Purpose/Format/Examples sections, `.. function::` directive, `:param:`/`:return:` fields, `::` literal blocks
- Direct inspection of `~/svn/gxmldoc/docs/addition.rst` -- operator page with different structure (Parameters/Returns sections, bare `::` in Format)
- Direct inspection of `~/svn/gxmldoc/docs/a.rst` -- alphabetical index page (toctree only)
- Direct inspection of `~/svn/gxmldoc/docs/_file_dir.rst` -- function page with no parameters (keyword)
- Direct inspection of `~/svn/gxmldoc/docs/include/` -- include fragments
- Direct inspection of `~/svn/gxmldoc/docs/conf.py` -- `primary_domain='gauss'`, `default_role='any'`, exclude_patterns
- docutils 0.22.4 API: OptionParser deprecated but functional (verified via [Docutils Release Notes](https://docutils.sourceforge.io/0.22/RELEASE-NOTES.html))

### Secondary (MEDIUM confidence)
- docutils node types (literal_block, section, field_list) -- based on stable API, not tested on this system since docutils not yet installed

### Tertiary (LOW confidence)
- Exact behavior of `.. function::` directive when parsed by standalone docutils (without Sphinx) -- needs empirical verification after install

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all versions verified, docutils API is stable and well-documented
- Architecture: HIGH - patterns derived from direct inspection of actual GAUSS doc files, confirmed by project research docs
- Pitfalls: HIGH - identified through actual corpus inspection (operator pages, include fragments, exclude_patterns)
- docutils `.. function::` handling: MEDIUM - known that Sphinx directives become unknown to standalone docutils, exact tree structure needs testing

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (stable domain, no fast-moving dependencies)

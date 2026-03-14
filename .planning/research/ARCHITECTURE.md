# Architecture Patterns

**Domain:** Documentation QA system (Sphinx RST, ~1,700 files, custom GAUSS domain)
**Researched:** 2026-03-14

## Recommended Architecture

Three-tier pipeline where each tier produces structured `Finding` objects, tiers run independently, and a report aggregator merges findings into unified output.

```
                    +------------------+
                    |   RST File Pool  |
                    | ~/svn/gxmldoc/   |
                    |   docs/ (~1,700) |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
     +--------v---+  +------v------+  +----v---------+
     |  Tier 1:   |  |  Tier 2:    |  |  Tier 3:     |
     | Structural |  | AI Persona  |  | Deep         |
     | Checks     |  | Reviews     |  | Validation   |
     | (docutils  |  | (Claude API)|  | (Claude API) |
     |  + Sphinx) |  |             |  |              |
     +--------+---+  +------+------+  +----+---------+
              |              |              |
              +--------------+--------------+
                             |
                    +--------v---------+
                    | Report Aggregator|
                    | (unified output) |
                    +------------------+
```

### Two Parsing Engines

This is the most important architectural decision. The system uses two distinct parsing approaches:

**1. docutils fast-parse (per-file, no Sphinx needed):**
```python
from docutils.utils import new_document
from docutils.parsers.rst import Parser
from docutils.frontend import OptionParser

parser = Parser()
settings = OptionParser(components=(Parser,)).get_default_values()
doc = new_document(filepath, settings)
parser.parse(rst_content, doc)
# Walk doc.traverse() for structural checks
```

Used for: code block presence, section structure, parameter completeness, directive validation. Fast -- processes all 1,700 files in seconds.

**2. Sphinx environment (full build, loads custom GAUSS domain):**
```python
from sphinx.application import Sphinx

app = Sphinx(
    srcdir="~/svn/gxmldoc/docs",
    confdir="~/svn/gxmldoc/docs",
    outdir="/tmp/gauss-qa-build",
    doctreedir="/tmp/gauss-qa-doctrees",
    buildername="dummy"  # or "html" if dummy not available
)
app.build()
env = app.env  # has resolved references, toctree, domain objects
```

Used for: cross-reference resolution, orphan detection, toctree graph, function registry. Takes 30-60 seconds but results can be cached.

### Component Boundaries

| Component | Responsibility | Inputs | Outputs |
|-----------|---------------|--------|---------|
| **File Inventory** | Scan docs dir, classify each RST by type | File system | `list[DocInfo]` with path, type, metadata |
| **RST Parser (docutils)** | Parse individual RST into doctree | Raw .rst content | `ParsedDoc` with sections, code blocks, directives, cross-refs |
| **Doc Classifier** | Determine doc type from path and content | File path, parsed content | `DocType` enum (command_ref, operator, alpha_index, guide, include_fragment) |
| **Sphinx Env Loader** | Load Sphinx build environment with GAUSS domain | docs directory | Sphinx `BuildEnvironment` with resolved refs |
| **Link Validator** | Detect broken cross-references | Sphinx env, parsed docs | `list[Finding]` |
| **Code Block Checker** | Verify code blocks exist and are non-empty | Parsed docs | `list[Finding]` |
| **Section Checker** | Verify required sections per doc type | Parsed docs, doc types | `list[Finding]` |
| **Signature Checker** | Verify param/return documentation completeness | Parsed docs (function directives) | `list[Finding]` |
| **Orphan Detector** | Find pages unreachable from toctree root | Sphinx env, file inventory | `list[Finding]` |
| **Glossary Enforcer** | Flag terminology deviations | Parsed docs, glossary YAML | `list[Finding]` |
| **Cross-Ref Counter** | Rank functions by reference frequency | All parsed docs | Ranked function list |
| **Auto-Fixer** | Apply safe mechanical fixes | Findings, raw RST | Fixed files + change log |
| **AI Persona Runner** | Batch AI reviews with persona prompts | Doc sections, persona configs | `list[Finding]` |
| **Deep Validator** | AI review of top-N function pages | Top-N RST files | `list[Finding]` |
| **Report Aggregator** | Merge all findings, render output | All `list[Finding]` | Terminal + JSON reports |

### Data Flow

```
Phase 1: Inventory & Parse (fast mode)
  File system scan -> file_inventory (all .rst paths + DocType classification)
  For each .rst -> docutils Parser -> ParsedDoc (sections, directives, code blocks, roles)

Phase 2: Tier 1 Structural Checks (docutils-based, fast)
  parsed_docs -> Code Block Checker -> findings
  parsed_docs + doc_types -> Section Checker -> findings
  parsed_docs -> Signature Checker -> findings
  parsed_docs + glossary.yaml -> Glossary Enforcer -> findings

Phase 3: Tier 1 Cross-Reference Checks (Sphinx-based, slower)
  Sphinx env load (with GAUSS domain) -> build_env
  build_env -> Link Validator -> findings
  build_env + file_inventory -> Orphan Detector -> findings
  build_env -> Cross-Ref Counter -> function_frequency.json

Phase 4: Auto-Fix (optional, after detection)
  findings (auto_fixable=True) + raw .rst -> Auto-Fixer -> fixed files + change_log.json

Phase 5: Tier 2 AI Persona Reviews
  Doc sections + persona configs -> AI Persona Runner -> findings

Phase 6: Tier 3 Deep Validation
  top_n_functions (from cross-ref counter) + RST source -> Deep Validator -> findings

Phase 7: Report Aggregation
  All findings -> Report Aggregator -> terminal output + report.json
```

### Key Data Structures

```python
from dataclasses import dataclass, field
from enum import Enum

class DocType(Enum):
    COMMAND_REF = "command_ref"       # Individual function pages (abs.rst, olsmt.rst)
    OPERATOR = "operator"             # Operator pages (addition.rst, assignment.rst)
    ALPHA_INDEX = "alpha_index"       # Letter index pages (a.rst, b.rst)
    GETTING_STARTED = "getting_started"
    USER_GUIDE = "user_guide"
    GRAPHICS_GUIDE = "graphics_guide"
    APP_MODULE = "app_module"         # tsmt/, fanpac/, cmlmt/, etc.
    INCLUDE_FRAGMENT = "include"      # include/ directory fragments
    OTHER = "other"

class Severity(Enum):
    ERROR = "error"       # Must fix: broken links, wrong signatures
    WARNING = "warning"   # Should fix: missing content, incomplete docs
    INFO = "info"         # May fix: style suggestions, minor issues

@dataclass
class CrossRef:
    role: str        # "func", "doc", "ref", "class", "any"
    target: str      # the reference target
    line_number: int
    resolved: bool = True  # set by link validator

@dataclass
class CodeBlock:
    content: str
    line_number: int
    is_empty: bool

@dataclass
class ParsedDoc:
    path: str
    doc_type: DocType
    title: str
    sections: list[str]
    function_directive: dict | None  # parsed .. function:: info
    code_blocks: list[CodeBlock]
    cross_refs: list[CrossRef]
    see_also: list[str]

@dataclass
class Finding:
    file: str
    line: int | None
    severity: Severity
    checker: str           # which component found this
    category: str          # "broken_link", "missing_code", "orphan", etc.
    message: str
    auto_fixable: bool = False
    fix_applied: bool = False
```

## Doc Type Classification

Critical to avoid false positives. Different page types have different required structures.

```python
def classify_doc(path: str, base_dir: str) -> DocType:
    rel = os.path.relpath(path, base_dir)
    parts = rel.split(os.sep)

    # Include fragments
    if "include" in parts:
        return DocType.INCLUDE_FRAGMENT

    # Subdirectory-based classification
    subdir_map = {
        "getting-started": DocType.GETTING_STARTED,
        "user-guide": DocType.USER_GUIDE,
        "graphics-guide": DocType.GRAPHICS_GUIDE,
        "tsmt": DocType.APP_MODULE,
        "fanpac": DocType.APP_MODULE,
        "cmlmt": DocType.APP_MODULE,
        "comt": DocType.APP_MODULE,
        # ... other app module dirs
    }
    for subdir, dtype in subdir_map.items():
        if subdir in parts:
            return dtype

    # Top-level files
    filename = os.path.basename(path)
    stem = os.path.splitext(filename)[0]

    # Single-letter files are alphabetical indexes
    if len(stem) == 1 and stem.isalpha():
        return DocType.ALPHA_INDEX

    # Operator pages (known list)
    operators = {"addition", "subtraction", "multiplication", "division",
                 "assignment", "address-operator", "dot-operators"}
    if stem in operators:
        return DocType.OPERATOR

    # Default: command reference function page
    return DocType.COMMAND_REF
```

**Required sections by type:**

| DocType | Required Sections |
|---------|-------------------|
| COMMAND_REF | Purpose, Format (with `.. function::`), Examples |
| OPERATOR | Purpose, Format, Examples |
| ALPHA_INDEX | (toctree only, no section requirements) |
| GETTING_STARTED | (flexible, no strict template) |
| USER_GUIDE | (flexible) |
| INCLUDE_FRAGMENT | (excluded from section checks) |

## Patterns to Follow

### Pattern 1: Uniform Finding Format
Every checker produces `Finding` objects with the same schema. The report aggregator merges, sorts, filters, and deduplicates without special-casing.

```python
findings.append(Finding(
    file="abs.rst",
    line=12,
    severity=Severity.ERROR,
    checker="link_validator",
    category="broken_link",
    message=":func:`nonexistent_function` target not found",
    auto_fixable=False
))
```

### Pattern 2: Checker Registration
Checkers register themselves and declare their parsing mode requirement.

```python
class BaseChecker:
    name: str
    requires_sphinx: bool = False  # True = needs Sphinx env

    def check(self, doc: ParsedDoc, **kwargs) -> list[Finding]:
        raise NotImplementedError
```

Fast-mode checkers (`requires_sphinx=False`) run in Phase 2. Sphinx-mode checkers run in Phase 3 after the environment is loaded.

### Pattern 3: CLI Subcommands
```bash
gauss-qa run                        # full pipeline (all tiers)
gauss-qa tier1                      # structural checks only
gauss-qa tier1 --check code-blocks  # single checker
gauss-qa tier1 --check links        # requires Sphinx env load
gauss-qa tier2 --persona newcomer   # single persona
gauss-qa tier3                      # deep validation (top-N)
gauss-qa top-n                      # show cross-ref frequency ranking
gauss-qa report                     # regenerate from cached findings
```

### Pattern 4: Cache Sphinx Environment
The Sphinx environment build is the slowest operation. Cache the pickled environment and doctrees between runs. Invalidate when any RST file is modified.

```python
# Store doctrees in a persistent location
DOCTREE_DIR = Path.home() / ".cache" / "gauss-doc-qa" / "doctrees"
BUILD_DIR = Path.home() / ".cache" / "gauss-doc-qa" / "build"
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Regex-Based RST Parsing
**What:** Using regular expressions to extract structure from RST.
**Why bad:** RST has context-dependent formatting. Regex misses nested directives, multi-line field lists, include fragments.
**Instead:** Use `docutils.parsers.rst.Parser` to parse into a document tree, then `document.traverse()` to walk it.

### Anti-Pattern 2: Monolithic Script
**What:** One giant Python script with all checks.
**Why bad:** Can't run individual checks, can't test components, can't iterate independently.
**Instead:** Separate modules per checker, unified Finding format, click CLI with subcommands.

### Anti-Pattern 3: Free-Text AI Output
**What:** Asking Claude to return prose reviews without structure.
**Why bad:** Can't aggregate, deduplicate, or prioritize findings programmatically.
**Instead:** Use structured output (JSON schema via tool_use) for all AI responses. Map to Finding dataclass.

### Anti-Pattern 4: Checking Built HTML
**What:** Running checks against `_build/html/` output.
**Why bad:** Sphinx silently suppresses some warnings. Built output masks source problems.
**Instead:** Parse RST source directly via docutils. Use Sphinx environment API for cross-refs.

### Anti-Pattern 5: Ignoring the Custom GAUSS Domain
**What:** Treating cross-references as standard Sphinx Python domain refs.
**Why bad:** The custom domain changes how `:func:`, bare backticks, and function signatures resolve. Standard resolution logic will produce false broken-link reports.
**Instead:** Load the full Sphinx environment which includes the GAUSS domain from `docs/util/GAUSSDomain.py`.

## Directory Structure

```
gauss-doc-qa/
├── pyproject.toml
├── src/
│   └── gauss_doc_qa/
│       ├── __init__.py
│       ├── cli.py                 # click CLI entry point
│       ├── config.py              # paths, defaults, settings
│       ├── models.py              # Finding, ParsedDoc, DocType, etc.
│       ├── parser/
│       │   ├── __init__.py
│       │   ├── rst_parser.py      # docutils-based RST parsing
│       │   ├── classifier.py      # doc type classification
│       │   ├── inventory.py       # file system scanning
│       │   └── sphinx_env.py      # Sphinx environment loader
│       ├── checkers/
│       │   ├── __init__.py
│       │   ├── base.py            # BaseChecker, checker registry
│       │   ├── code_blocks.py     # code block presence/emptiness
│       │   ├── sections.py        # required section validation
│       │   ├── signatures.py      # param/return completeness
│       │   ├── links.py           # cross-reference validation (Sphinx)
│       │   ├── orphans.py         # orphan page detection (Sphinx)
│       │   ├── glossary.py        # terminology consistency
│       │   └── cross_ref_count.py # frequency analysis for top-N
│       ├── fixer/
│       │   ├── __init__.py
│       │   └── auto_fixer.py      # safe mechanical fixes
│       ├── ai/
│       │   ├── __init__.py
│       │   ├── personas.py        # persona configs and prompts
│       │   ├── batch_runner.py    # Claude API submission
│       │   ├── deep_validator.py  # top-N deep validation
│       │   └── schemas.py         # structured output schemas
│       └── report/
│           ├── __init__.py
│           ├── aggregator.py      # merge all findings
│           └── renderer.py        # rich terminal + JSON output
├── config/
│   ├── personas/
│   │   ├── newcomer.yaml
│   │   ├── expert.yaml
│   │   ├── translator.yaml
│   │   └── editor.yaml
│   └── glossary.yaml              # canonical terminology
├── tests/
│   ├── fixtures/                  # sample RST files for testing
│   ├── test_parser.py
│   ├── test_classifier.py
│   ├── test_code_blocks.py
│   ├── test_sections.py
│   └── test_links.py
└── reports/                       # output directory (gitignored)
    └── .gitkeep
```

## Scalability Considerations

| Concern | Current (~1,700 files) | At 5,000 files | At 10,000+ files |
|---------|----------------------|-----------------|-------------------|
| docutils parse | <10 seconds | ~30 seconds | Use ProcessPoolExecutor |
| Sphinx env load | 30-60 seconds | 60-120 seconds | Cache aggressively |
| Memory | ~100MB (all ParsedDocs) | ~300MB | Stream-process if needed |
| Link validation | O(files * refs), manageable | Build inverted index | Same |
| AI API calls | ~36 calls (16 persona + 20 deep) | Same (sampling) | Same |
| Report size | <1000 findings | Filter by severity | Separate reports per section |

For 1,700 files, everything fits in a single-process Python script. No databases, queues, or distributed processing needed.

## Sources

- Direct inspection of `~/svn/gxmldoc/docs/` corpus (1,716 RST files, 30+ directories)
- Sphinx conf.py: `primary_domain='gauss'`, `default_role='any'`, custom domain/roles/translator in `docs/util/`
- GAUSSDomain.py: custom function signature regex, GAUSS-specific reference resolution
- RST file patterns: `abs.rst` (standard function page), `olsmt.rst` (complex with seealso), letter index pages
- docutils parsing API: HIGH confidence (stable, well-documented, core dependency of Sphinx)

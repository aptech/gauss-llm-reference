# Technology Stack

**Project:** GAUSS Documentation QA System
**Researched:** 2026-03-14

## Recommended Stack

### Core: RST Parsing and Sphinx Integration

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| Python | 3.14 | Runtime | Already installed on the system | HIGH (verified) |
| docutils | 0.22.4 | Low-level RST parsing, AST traversal | The canonical RST parser. Sphinx itself is built on it. Use directly for structural checks (code blocks, sections, directives) without needing a full Sphinx build | HIGH (version verified via pip index) |
| sphinx | 9.1.0 | Cross-reference resolution, toctree analysis | The docs already use Sphinx 9.x with a custom GAUSS domain (`GAUSSDomain.py` in `docs/util/`). Sphinx's `Environment` API resolves `:func:`, `:ref:`, `:doc:` references using the actual domain configuration. Docutils alone cannot resolve Sphinx cross-references | HIGH (version verified via pip index) |

**Key architectural decision:** Use docutils for fast per-file structural checks (code block presence, section structure, RST syntax). Use Sphinx's build environment for cross-reference and toctree analysis, which requires the full domain registry.

The GAUSS docs have a custom Sphinx domain (`GAUSSDomain.py`) that registers `:func:` roles for GAUSS functions, plus custom roles (`GAUSSRoles.py`) and a custom HTML translator. The `conf.py` sets `primary_domain = 'gauss'` and `default_role = 'any'`, meaning bare backtick references resolve through the GAUSS domain. Cross-reference validation must load this domain, which means using Sphinx's API -- not just docutils.

**Two parsing modes:**

1. **Fast mode (docutils only):** Parse individual RST files into docutils ASTs. Check structural properties: section hierarchy, code block presence/non-emptiness, parameter documentation completeness. No Sphinx needed. Runs in seconds on 1,700 files.

2. **Full mode (Sphinx environment):** Run a Sphinx build (or load a cached environment) to get the resolved cross-reference index, toctree structure, and domain object registry. Required for broken link detection, orphan page detection, cross-reference frequency analysis. Takes 30-60 seconds for initial build, faster with caching.

### AI Integration

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| anthropic | >=0.84.0 | Batch AI persona reviews and deep function validation | Already installed locally (0.84.0). Claude is well-suited for doc review -- strong at identifying unclear explanations, missing context, inconsistent terminology. Use the Messages API with structured output for each review pass | HIGH (version verified installed) |

**Why not OpenAI or other providers:** The project runs in a Claude-centric environment. The anthropic SDK is installed. No reason to add another provider's SDK or a multi-provider abstraction.

**Batch strategy:** Use the Anthropic Messages API directly. For ~16 persona-section combinations plus ~20 deep validations, sequential calls with rate limiting are sufficient. Use structured output (tool_use or JSON mode) so findings parse cleanly into the Finding dataclass.

### Terminology and Fuzzy Matching

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| rapidfuzz | 3.14.3 | Fuzzy string matching for terminology checking | C-extension performance (10-100x faster than fuzzywuzzy). Needed for matching ~1,700 files against a canonical glossary. Levenshtein ratio catches typos like "gaussian" vs "Gaussian", "time-series" vs "time series" | HIGH (version verified via pip index) |

### CLI and Reporting

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| rich | 14.3.3 | Terminal output formatting, progress bars, severity-colored tables | Makes batch processing of 1,700 files readable. Already installed | HIGH (version verified via pip index) |
| click | 8.3.1 | CLI framework with subcommands | Clean structure: `gauss-qa tier1 --check links`, `gauss-qa tier2 --persona newcomer`. Already installed | HIGH (version verified installed) |
| PyYAML | 6.0.3 | Configuration files (glossary, persona definitions) | Standard YAML parser. Already installed | HIGH (version verified installed) |

### Standard Library (No Install Needed)

| Module | Purpose | Why |
|--------|---------|-----|
| json | Report output, cross-reference index caching | Machine-readable reports, cache Sphinx environment results |
| pathlib | File path handling | Cleaner than os.path for recursive directory traversal |
| dataclasses | Internal data models (Finding, ParsedDoc, CrossRef) | Lightweight typed containers. This is an internal tool, not an API -- pydantic is overkill |
| concurrent.futures | Optional parallel parsing | ProcessPoolExecutor for parsing 1,700 files if sequential is too slow |
| re | Regex for content-level terminology matching | Used within already-parsed text nodes, never for RST structure |

### Testing

| Technology | Version | Purpose | Why | Confidence |
|------------|---------|---------|-----|------------|
| pytest | >=8.0 | Test runner | Standard. Test each checker in isolation against fixture RST files | HIGH |

## What NOT to Use

| Technology | Why Not |
|------------|---------|
| **pydantic** | Overkill for internal data models. dataclasses are sufficient -- no API boundary validation needed |
| **pandas** | No tabular data analysis. This processes text files and produces reports |
| **Beautiful Soup / lxml** | RST is not HTML. Docutils provides the correct AST |
| **rst2html + HTML parsing** | Roundtrip through HTML loses RST-level information (directive types, role references) |
| **rstcheck** | Checks RST syntax errors only. Cannot do semantic checks (cross-ref validity, terminology, code block content) |
| **sphinx-build CLI (shelling out)** | Don't shell out. Use Sphinx's Python API (`sphinx.application.Sphinx`) to get the build environment programmatically |
| **fuzzywuzzy** | Superseded by rapidfuzz. Slower, GPL licensing issues (python-Levenshtein dependency) |
| **Jinja2** | Reports are terminal output (rich) or JSON. No HTML templating needed |
| **SQLite** | JSON file cache is sufficient for the cross-reference index. 1,700 files does not warrant a database |
| **typer** | click is simpler and already installed. Typer adds a typing-extensions dependency for no real benefit here |
| **litellm / multi-provider abstraction** | Single AI provider (Claude). Abstraction layer adds complexity with zero benefit |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| RST parsing | docutils 0.22.4 | regex/string parsing | RST is whitespace-sensitive with nested directives. Regex misses edge cases and produces false positives |
| Cross-ref resolution | Sphinx Python API | Manual regex for `:func:` roles | Cannot resolve references through the custom GAUSS domain. Sphinx already does this correctly |
| Cross-ref resolution | Sphinx Python API | Sphinx `-b linkcheck` CLI | linkcheck only validates external URLs, not internal cross-references |
| Fuzzy matching | rapidfuzz | thefuzz (fuzzywuzzy fork) | rapidfuzz is faster and more actively maintained |
| CLI framework | click | argparse | Subcommand structure is cleaner with click |
| AI provider | anthropic SDK | openai SDK | Already in a Claude environment. Switching providers adds zero value |
| Config format | YAML | TOML | Either works. YAML is slightly more natural for multi-line persona prompt definitions |

## Installation

```bash
# Core dependencies
pip install docutils==0.22.4 sphinx==9.1.0 anthropic>=0.84.0

# Utility dependencies
pip install rapidfuzz==3.14.3 rich==14.3.3 click==8.3.1 pyyaml==6.0.3

# Dev dependencies
pip install pytest>=8.0
```

Or as `pyproject.toml`:

```toml
[project]
name = "gauss-doc-qa"
requires-python = ">=3.12"
dependencies = [
    "docutils>=0.22",
    "sphinx>=9.0",
    "anthropic>=0.84",
    "rapidfuzz>=3.14",
    "rich>=14.0",
    "click>=8.3",
    "pyyaml>=6.0",
]

[project.optional-dependencies]
dev = ["pytest>=8.0"]

[project.scripts]
gauss-qa = "gauss_doc_qa.cli:main"
```

## Sources

- docutils 0.22.4: Verified via `pip3 index versions docutils` (latest as of 2026-03-14)
- Sphinx 9.1.0: Verified via `pip3 index versions sphinx` (latest as of 2026-03-14)
- anthropic 0.84.0: Verified installed locally via `pip3 index versions anthropic`
- rapidfuzz 3.14.3: Verified via `pip3 index versions rapidfuzz`
- rich 14.3.3: Verified via `pip3 index versions rich`
- click 8.3.1: Verified installed locally
- PyYAML 6.0.3: Verified installed locally
- Python 3.14.2: Verified via `python3 --version`
- Custom GAUSS Sphinx domain: Inspected at `~/svn/gxmldoc/docs/util/GAUSSDomain.py`
- Sphinx conf.py: Inspected at `~/svn/gxmldoc/docs/conf.py` -- confirms custom domain, lexer, roles, `primary_domain='gauss'`, `default_role='any'`

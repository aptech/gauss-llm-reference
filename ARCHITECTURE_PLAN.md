# GAUSS LLM Reference: Long-Term Architecture Plan

## Overview

This document outlines the evolution of the GAUSS LLM reference from static markdown files to a structured, RAG-ready knowledge base that can serve multiple output formats.

## Current State

```
gauss-llm-reference/
├── CLAUDE.md                  # Main reference (~16KB)
└── .claude/gauss/
    ├── dataframes.md
    ├── structures.md
    ├── strings.md
    ├── graphics.md
    ├── io.md
    ├── timeseries.md
    ├── panel.md
    ├── matrices.md
    └── apps/
        ├── tsmt.md
        ├── fanpac.md
        ├── cointegration.md
        └── garch.md
```

**Strengths:**
- Simple, works today
- Good content coverage
- Effective gotchas section

**Limitations:**
- All content loaded regardless of task (token inefficient)
- No semantic chunking for retrieval
- No metadata for filtering/prioritization
- Single output format (static markdown)

## Target Architecture

### Directory Structure

```
gauss-llm-reference/
├── source/                    # SINGLE SOURCE OF TRUTH
│   ├── schema.yaml            # Chunk structure definition
│   ├── core/                  # Core language syntax
│   │   ├── operators.yaml
│   │   ├── control-flow.yaml
│   │   ├── procedures.yaml
│   │   └── data-types.yaml
│   ├── gotchas/               # Common mistakes (high priority)
│   │   ├── matrix-multiply.yaml
│   │   ├── string-operators.yaml
│   │   ├── indexing.yaml
│   │   └── ...
│   ├── stdlib/                # Standard library functions
│   │   ├── io/
│   │   │   ├── loadd.yaml
│   │   │   ├── saved.yaml
│   │   │   └── ...
│   │   ├── matrix/
│   │   ├── stats/
│   │   └── ...
│   ├── patterns/              # Common code patterns
│   │   ├── data-cleaning.yaml
│   │   ├── regression.yaml
│   │   └── ...
│   └── apps/                  # Application modules
│       ├── tsmt/
│       ├── fanpac/
│       └── ...
│
├── build/                     # GENERATED OUTPUTS (gitignored)
│   ├── claude-code/           # Static context files
│   │   ├── CLAUDE.md
│   │   └── gauss/*.md
│   ├── embeddings/            # Vector search ready
│   │   ├── chunks.jsonl
│   │   └── metadata.json
│   ├── mcp/                   # MCP server data
│   │   └── reference.db
│   └── docs/                  # Human documentation
│       └── site/
│
├── scripts/
│   ├── build.py               # Main build orchestrator
│   ├── build_claude_code.py   # Generate static markdown
│   ├── build_embeddings.py    # Generate vector chunks
│   ├── validate.py            # Schema and content validation
│   └── test_examples.py       # Verify code examples work
│
├── templates/                 # Output templates
│   ├── CLAUDE.md.j2
│   └── topic.md.j2
│
├── tests/
│   └── ...
│
├── CLAUDE.md                  # Symlink → build/claude-code/CLAUDE.md
├── .claude/                   # Symlink → build/claude-code/gauss/
├── pyproject.toml
└── README.md
```

### Source Schema

Each knowledge chunk follows a consistent YAML schema:

```yaml
# source/schema.yaml
chunk:
  required:
    - id            # Unique identifier (e.g., "gotcha-matrix-mult")
    - type          # gotcha | function | pattern | concept | operator
    - title         # Human-readable title
    - summary       # 1-2 sentence description
    - content       # Main content with code examples

  optional:
    - priority      # critical | high | medium | low
    - keywords      # List of search terms
    - related       # List of related chunk IDs
    - comparison    # Equivalents in other languages
    - wrong         # Incorrect code example (for gotchas)
    - right         # Correct code example (for gotchas)
    - parameters    # Function parameters (for functions)
    - returns       # Return value description (for functions)
    - examples      # Additional usage examples
    - see_also      # External references
    - since         # GAUSS version introduced
    - deprecated    # Deprecation info if applicable
```

### Example Source Chunk

```yaml
# source/gotchas/matrix-multiply.yaml
id: gotcha-matrix-mult
type: gotcha
priority: critical
title: "Matrix vs Element-wise Multiplication"

keywords:
  - multiply
  - element-wise
  - dot product
  - ".*"
  - "*"
  - matrix multiplication
  - hadamard

related:
  - gotcha-matrix-division
  - op-arithmetic
  - op-element-wise

summary: |
  In GAUSS, `*` is matrix multiplication, NOT element-wise.
  Use `.*` for element-wise multiplication.

wrong:
  code: |
    a = { 1 2, 3 4 };
    b = { 2 2, 2 2 };
    c = a * b;     // Matrix multiply, NOT element-wise!
  result: "Matrix product, not {2 4, 6 8}"

right:
  code: |
    a = { 1 2, 3 4 };
    b = { 2 2, 2 2 };
    c = a .* b;    // Element-wise: {2 4, 6 8}
  result: "{2 4, 6 8}"

comparison:
  python:
    element_wise: "a * b"
    matrix: "a @ b"
    note: "Opposite of GAUSS - * is element-wise in NumPy"
  matlab:
    element_wise: "a .* b"
    matrix: "a * b"
    note: "Same as GAUSS"
  r:
    element_wise: "a * b"
    matrix: "a %*% b"
    note: "Opposite of GAUSS"

content: |
  ## The Problem

  Users coming from Python/NumPy or R expect `*` to be element-wise.
  In GAUSS (like MATLAB), `*` performs matrix multiplication.

  ## The Rule

  | Operator | Operation |
  |----------|-----------|
  | `*` | Matrix multiplication |
  | `.*` | Element-wise multiplication |
  | `/` | Matrix division (right) |
  | `./` | Element-wise division |
  | `^` | Matrix power |
  | `.^` | Element-wise power |

  The dot prefix (`.`) always means element-wise.
```

### Example Function Chunk

```yaml
# source/stdlib/io/loadd.yaml
id: fn-loadd
type: function
title: "loadd - Load Data File"
priority: high

keywords:
  - load
  - read
  - csv
  - excel
  - stata
  - import
  - data

summary: |
  Loads data from various file formats (CSV, Excel, Stata, SAS, SPSS, HDF5)
  into a GAUSS dataframe.

signature: "df = loadd(filename[, formula])"

parameters:
  - name: filename
    type: string
    description: "Path to data file. Format auto-detected from extension."
  - name: formula
    type: string
    optional: true
    description: "Formula string specifying columns and transformations."

returns:
  type: dataframe
  description: "Dataframe containing loaded data"

examples:
  - description: "Load entire CSV file"
    code: |
      df = loadd("mydata.csv");

  - description: "Load specific columns"
    code: |
      df = loadd("mydata.csv", "Age + Income + Gender");

  - description: "Load all except certain columns"
    code: |
      df = loadd("mydata.csv", ". - ID - Timestamp");

  - description: "Load with type specifications"
    code: |
      df = loadd("mydata.csv", "date(OrderDate) + cat(Region) + Amount");

related:
  - fn-saved
  - fn-csvreadm
  - concept-formula-strings
  - concept-dataframes

see_also:
  - title: "Formula String Reference"
    url: "#formula-strings"
```

## Build Outputs

### 1. Claude Code (Static Markdown)

Generated `CLAUDE.md` includes:
- Core syntax quick reference (always)
- Critical gotchas (always)
- Comparison tables (always)
- Condensed topic summaries

Generated `.claude/gauss/*.md` files contain full topic details.

**Token budget:** ~15-20K tokens total

### 2. Embeddings (RAG)

`chunks.jsonl`:
```json
{"id": "gotcha-matrix-mult", "text": "Matrix vs element-wise...", "embedding": [...]}
{"id": "fn-loadd", "text": "loadd - Load data from CSV...", "embedding": [...]}
```

**Chunk size target:** 200-500 tokens per chunk

### 3. MCP Server

SQLite database with:
- Full chunk content
- Metadata for filtering
- Full-text search index
- Embedding vectors (optional)

### 4. Human Documentation

Static site (MkDocs/Sphinx) generated from same sources.

## Migration Plan

### Phase 1: Foundation (Week 1-2)

**Goal:** Establish schema and tooling without changing outputs

Tasks:
- [ ] Define YAML schema (`source/schema.yaml`)
- [ ] Create build script skeleton
- [ ] Convert critical gotchas to YAML (5-10 chunks)
- [ ] Build generates identical `CLAUDE.md` output
- [ ] Add schema validation

Validation:
- `diff` between generated and current `CLAUDE.md` should be minimal
- All code examples parse successfully

### Phase 2: Core Content (Week 3-4)

**Goal:** Convert all existing content to structured sources

Tasks:
- [ ] Convert `CLAUDE.md` quick reference sections
- [ ] Convert all `.claude/gauss/*.md` topic files
- [ ] Add cross-references (`related` fields)
- [ ] Add language comparison data
- [ ] Build full validation suite

Deliverable:
- 100% of content in YAML sources
- Build generates all current outputs

### Phase 3: Enhanced Retrieval (Month 2)

**Goal:** Enable smart retrieval beyond static loading

Tasks:
- [ ] Implement embeddings pipeline
- [ ] Create MCP server prototype
- [ ] Add retrieval benchmarks
- [ ] Test with real queries

Deliverable:
- Working RAG pipeline
- MCP tool for GAUSS lookups

### Phase 4: Optimization (Ongoing)

**Goal:** Continuous improvement based on usage

Tasks:
- [ ] Add usage analytics
- [ ] Track retrieval effectiveness
- [ ] A/B test chunk sizes
- [ ] Expand coverage based on gaps
- [ ] User feedback integration

## Design Decisions

### Why YAML over JSON?
- More readable for content with multiline strings
- Supports comments for internal notes
- Easier to edit manually

### Why not a database?
- Sources should be version-controlled
- Plain text enables easy review/diff
- Build step creates optimized formats for each use case

### Chunk size guidelines
- **Gotchas:** 100-300 tokens (focused, retrievable)
- **Functions:** 200-500 tokens (signature + examples)
- **Patterns:** 300-600 tokens (full context needed)
- **Concepts:** 400-800 tokens (explanatory)

### Priority levels
- **critical:** Always loaded in static context
- **high:** Loaded for relevant topics
- **medium:** Retrieved on demand
- **low:** Available but rarely needed

## Success Metrics

1. **Token efficiency:** 50%+ reduction in average context used
2. **Retrieval precision:** >90% relevant chunks for test queries
3. **Code quality:** Fewer GAUSS syntax errors in generated code
4. **Coverage:** All common functions/patterns documented
5. **Freshness:** New GAUSS features documented within 1 week

## Open Questions

1. **Embedding model:** Which model for chunk embeddings?
   - OpenAI `text-embedding-3-small` (cheap, good)
   - Anthropic embeddings (when available)
   - Local model for offline use

2. **MCP vs native RAG:** Will Claude Code get native RAG?
   - Design for MCP now, migrate if native arrives

3. **Multi-language:** Support translations?
   - Defer until English is complete

4. **Community contributions:** Accept PRs?
   - Need validation pipeline first

## References

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Specification](https://modelcontextprotocol.io)
- [GAUSS Documentation](https://docs.aptech.com)

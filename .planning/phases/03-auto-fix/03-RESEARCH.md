# Phase 3: Auto-Fix - Research

**Researched:** 2026-03-14
**Domain:** RST documentation auto-correction with dry-run safety and Sphinx build verification
**Confidence:** HIGH

## Summary

Phase 3 adds conservative auto-fix capabilities to the gauss-doc-qa tool. The scope is deliberately narrow: fix broken internal links (`:func:`, `:doc:`) where the correct target is unambiguously determinable, with dry-run as the default mode and Sphinx build verification to confirm no RST corruption.

The existing codebase provides all the detection infrastructure needed. The `LinksChecker` and `SeeAlsoChecker` already identify broken cross-references with file path and line number. The `Finding` model already has an `auto_fixable` field (defaulting to `False`). The Sphinx environment loader provides the GAUSS domain object registry for target resolution. What's missing is: (1) a fix resolution strategy that maps broken targets to correct ones, (2) a safe RST file editor that only touches leaf text, (3) a dry-run/apply CLI workflow, and (4) Sphinx build verification.

**Primary recommendation:** Build a thin `fixer/` module with three components: a `FixProposal` dataclass (old text, new text, line, file), a `resolve_fix()` function that uses fuzzy matching against the GAUSS domain object registry to find unambiguous corrections, and an `apply_fixes()` function that edits raw RST lines while enforcing the leaf-text-only safety constraint. Add a `fix` CLI subcommand with `--apply` flag (dry-run by default) and `--verify` flag for post-fix Sphinx build.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| FIXR-01 | Auto-fix for broken internal links where target can be unambiguously determined | Fuzzy matching against GAUSS domain objects registry (case-insensitive, edit-distance) provides unambiguous resolution. Links checker already detects broken refs with line numbers. |
| FIXR-02 | Auto-fix runs in dry-run mode by default, showing proposed changes without applying | New `fix` CLI subcommand defaults to dry-run. Uses `--apply` flag to write changes. Rich diff output for dry-run preview. |
| FIXR-03 | Auto-fix only modifies leaf text nodes, never tables or directive structures | Line-level safety check: reject fixes on lines inside table markers, directive arguments, or code blocks. Detect via RST structural patterns (indentation under directives, table grid/simple markers, literal block indentation). |
| FIXR-04 | Sphinx build verification available after auto-fix to confirm no RST corruption | `--verify` flag on the fix command runs `load_sphinx_env()` post-fix and checks for new warnings. Compare warning counts before/after. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| difflib | stdlib | SequenceMatcher for fuzzy string matching | Built-in, no dependency needed for edit-distance-like matching against function registry |
| pathlib | stdlib | File path handling and safe file I/O | Already used throughout codebase |
| click | 8.3+ | CLI subcommand for `fix` | Already a project dependency, used for existing commands |
| rich | 14.0+ | Diff-style output for dry-run preview | Already a project dependency |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| sphinx | 9.0+ | Build verification post-fix | Already a dependency; reuse `load_sphinx_env()` for verification |
| re | stdlib | RST role reference pattern matching | Already used in links.py and seealso.py |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| difflib.SequenceMatcher | rapidfuzz | Better performance but adds dependency; not needed for ~1700 function names |
| Line-level text replacement | docutils tree manipulation + serialization | Safer in theory but docutils does not preserve original RST formatting on serialization -- would corrupt whitespace |

## Architecture Patterns

### Recommended Module Structure
```
gauss-doc-qa/src/gauss_doc_qa/
  fixer/
    __init__.py
    models.py          # FixProposal dataclass
    resolver.py         # resolve broken refs to correct targets
    applier.py          # apply fixes to RST files with safety checks
    verify.py           # Sphinx build verification
```

### Pattern 1: FixProposal as Immutable Data
**What:** Each proposed fix is a dataclass with all information needed to preview and apply it.
**When to use:** Always -- every fix flows through this model.
**Example:**
```python
@dataclass
class FixProposal:
    file_path: str
    line_number: int
    original_text: str      # the full line containing the broken ref
    fixed_text: str          # the line with corrected ref
    old_target: str          # e.g., "plotbar"
    new_target: str          # e.g., "plotBar"
    category: str            # "broken_func_ref", "broken_doc_ref", etc.
    confidence: float        # 0.0-1.0 fuzzy match score
    finding: Finding         # the original Finding that triggered this
```

### Pattern 2: Resolution Strategy for Broken :func: References
**What:** Use the GAUSS domain object registry (case-insensitive lookup already exists via `casefold()`) plus fuzzy matching for typos.
**When to use:** For every broken `:func:` reference found by LinksChecker or SeeAlsoChecker.
**Strategy:**
1. Case-insensitive exact match -- the GAUSS domain already does this in `_search_objects`, but the checker uses its own `casefold()` dict. If the checker reports it as broken, it truly does not exist.
2. Fuzzy match via `difflib.get_close_matches()` against the full object registry. Accept only if exactly ONE match scores above threshold (e.g., 0.85).
3. If zero or multiple matches, the fix is ambiguous -- mark as not auto-fixable.

### Pattern 3: Leaf Text Safety Check
**What:** Before applying a fix to a line, verify the line is safe to modify.
**When to use:** Every fix application.
**Rules -- a line is UNSAFE if:**
- It is inside a literal block (indented under `::` or inside `.. code-block::`)
- It matches table grid markers (`+---+`, `|...|`) or simple table underlines (`===`, `---`)
- It is a directive argument line (starts with `.. ` followed by directive name)
- It is inside a field list that is part of a `.. function::` directive body

**Rules -- a line is SAFE if:**
- It contains a `:func:` or `:doc:` role reference in flowing paragraph text
- It is inside a `.. seealso::` body (these are paragraph-level)
- The replacement only changes the target string inside backticks, not surrounding structure

### Pattern 4: Dry-Run as Default with Rich Diff
**What:** Default behavior shows colored diff of proposed changes. `--apply` flag writes to disk.
**When to use:** Always -- the `fix` CLI subcommand.
**Example output:**
```
--- docs/acf.rst (line 152)
-   .. seealso:: Functions :func:`plotbar`
+   .. seealso:: Functions :func:`plotBar`
   [confidence: 0.92, category: broken_func_ref]

Proposed fixes: 3 (2 high confidence, 1 medium)
Run with --apply to write changes.
```

### Anti-Patterns to Avoid
- **Tree-based RST rewriting:** docutils cannot round-trip RST faithfully. Parsing then serializing back changes whitespace, directive formatting, and comment blocks. All fixes must operate on raw text lines.
- **Fixing inside code blocks:** Even if a code block contains a function name that looks wrong, code blocks are executable examples and must not be modified by auto-fix.
- **Multi-line fixes:** Stick to single-line replacements only. A `:func:` reference that spans lines (rare but possible) should be skipped.
- **Fixing without the original Finding:** Every fix must trace back to a Finding from the detection phase. Do not scan for fixable patterns independently.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Fuzzy string matching | Custom Levenshtein | `difflib.get_close_matches()` | Handles scoring, thresholds, and returns ranked matches. Sufficient for ~1700 function names. |
| RST parsing for safety checks | Regex-based RST parser | Line-context heuristics + existing ParsedDoc | Only need to know "is this line inside a code block or table" -- don't need full parse. Use code_blocks from ParsedDoc for line ranges. |
| Sphinx build verification | Custom RST validator | `load_sphinx_env()` from existing sphinx_env.py | Already builds with the GAUSS domain. Check warning count before/after. |
| CLI subcommand framework | Manual argparse | click (already used) | Consistent with existing `scan` and `check-refs` commands. |

## Common Pitfalls

### Pitfall 1: Corrupting RST Whitespace During Fix Application
**What goes wrong:** String replacement changes line length inside a table cell or shifts indentation in a directive body.
**Why it happens:** RST is whitespace-sensitive. A fix that changes `:func:`plotbar`` to `:func:`plotBar`` is safe in flowing text but dangerous inside a grid table cell.
**How to avoid:** Enforce leaf-text-only constraint. Check that the fix line is not inside a table or directive structure. Only replace the exact role reference pattern, preserving all surrounding text.
**Warning signs:** Sphinx build produces new warnings after fix application.

### Pitfall 2: Ambiguous Fuzzy Matches Creating Wrong Fixes
**What goes wrong:** "plotbar" matches both "plotBar" and "plotBars" at similar confidence. Auto-fix picks one and creates a wrong reference.
**Why it happens:** Fuzzy matching returns multiple candidates when function names are similar.
**How to avoid:** Require exactly ONE match above threshold for auto-fix. If multiple candidates score similarly (within 0.05 of each other), mark as ambiguous and skip. Log skipped fixes for manual review.
**Warning signs:** Post-fix Sphinx build shows the "fixed" reference is still broken.

### Pitfall 3: Fixing References That Are Intentionally Different
**What goes wrong:** A `:func:` reference to a function that genuinely doesn't exist (e.g., documenting a planned feature, or referencing an application module function not in the base domain) gets "corrected" to a similar-sounding but wrong function.
**Why it happens:** The resolver assumes all broken refs are typos.
**How to avoid:** Set a high fuzzy match threshold (0.85+). Require the match to be unambiguous (single candidate). In dry-run output, clearly show the proposed change so a human can reject it before applying.

### Pitfall 4: Modifying Files with Uncommitted Changes
**What goes wrong:** Auto-fix overwrites local edits that haven't been committed.
**Why it happens:** The tool writes directly to files in the working copy.
**How to avoid:** Not in v1 scope (SVN status checking is a nice-to-have), but the dry-run default prevents accidental writes. The `--apply` flag makes it explicit.

### Pitfall 5: Re-reading Files After Modification
**What goes wrong:** When applying multiple fixes to the same file, line numbers shift after the first fix.
**Why it happens:** Fixes are applied sequentially and earlier fixes change line count.
**How to avoid:** Group fixes by file. For each file, apply all fixes in a single pass from bottom to top (highest line number first). Since we only do single-line replacements (no line insertions/deletions), line numbers actually remain stable. But process bottom-up as a safety measure.

## Code Examples

### Fix Resolution
```python
import difflib

def resolve_func_ref(broken_target: str, gauss_objects: dict) -> tuple[str, float] | None:
    """Find unambiguous correction for a broken :func: reference.

    Returns (correct_name, confidence) or None if ambiguous/no match.
    """
    # Get all known function names
    known_names = list(gauss_objects.keys())

    # Find close matches (case-insensitive comparison)
    matches = difflib.get_close_matches(
        broken_target.casefold(),
        [n.casefold() for n in known_names],
        n=3,
        cutoff=0.85,
    )

    if len(matches) == 1:
        # Map back to original casing
        cf_to_orig = {n.casefold(): n for n in known_names}
        correct_name = cf_to_orig[matches[0]]
        ratio = difflib.SequenceMatcher(
            None, broken_target.casefold(), matches[0]
        ).ratio()
        return (correct_name, ratio)

    if len(matches) >= 2:
        # Check if top match is clearly better
        ratios = [
            difflib.SequenceMatcher(None, broken_target.casefold(), m).ratio()
            for m in matches
        ]
        if ratios[0] - ratios[1] > 0.05:
            cf_to_orig = {n.casefold(): n for n in known_names}
            return (cf_to_orig[matches[0]], ratios[0])

    return None  # Ambiguous or no match
```

### Leaf Text Safety Check
```python
import re

# Table markers
TABLE_GRID_RE = re.compile(r"^\s*[+|][-=+|]+[+|]\s*$")
TABLE_SIMPLE_RE = re.compile(r"^\s*[=]+(\s+[=]+)+\s*$")

# Directive line
DIRECTIVE_RE = re.compile(r"^\s*\.\.\s+\w+")

def is_safe_to_fix(line: str, line_num: int, parsed_doc) -> bool:
    """Check if a line is safe to modify (leaf text only)."""
    # Reject table markers
    if TABLE_GRID_RE.match(line) or TABLE_SIMPLE_RE.match(line):
        return False

    # Reject table cell content (starts with |)
    if line.strip().startswith("|"):
        return False

    # Reject directive argument lines
    if DIRECTIVE_RE.match(line) and "seealso" not in line.lower():
        return False

    # Reject lines inside code blocks
    for cb in parsed_doc.code_blocks:
        if cb.line_number and abs(cb.line_number - line_num) < 2:
            # Too close to a code block boundary -- need more precise check
            pass
    # More precise: check if line_num falls within any literal_block range
    # (requires tracking end lines of code blocks, which we can compute)

    return True
```

### CLI Subcommand
```python
@cli.command()
@click.option("--apply", is_flag=True, default=False,
              help="Apply fixes (default is dry-run)")
@click.option("--verify", is_flag=True, default=False,
              help="Run Sphinx build verification after applying fixes")
@click.option("--min-confidence", type=float, default=0.85,
              help="Minimum fuzzy match confidence for auto-fix")
@click.pass_context
def fix(ctx, apply, verify, min_confidence):
    """Auto-fix broken internal links (dry-run by default)."""
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Regex find-replace in RST | AST-guided detection + line-level text fix | Standard practice | Prevents structural corruption |
| Fix everything possible | Conservative whitelist of fixable categories | Standard practice | Prevents false corrections |
| Apply immediately | Dry-run default with explicit apply flag | Standard practice | Safety net for documentation teams |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | none (uses pyproject.toml discovery) |
| Quick run command | `python -m pytest gauss-doc-qa/tests/ -x -q` |
| Full suite command | `python -m pytest gauss-doc-qa/tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| FIXR-01 | Broken func ref resolved to correct target via fuzzy match | unit | `pytest gauss-doc-qa/tests/test_resolver.py -x` | Wave 0 |
| FIXR-01 | Ambiguous matches (multiple candidates) are skipped | unit | `pytest gauss-doc-qa/tests/test_resolver.py -x` | Wave 0 |
| FIXR-01 | Fix applied correctly to RST line text | unit | `pytest gauss-doc-qa/tests/test_applier.py -x` | Wave 0 |
| FIXR-02 | Dry-run mode shows diff without modifying files | unit | `pytest gauss-doc-qa/tests/test_fix_cli.py -x` | Wave 0 |
| FIXR-02 | --apply flag writes changes to disk | unit | `pytest gauss-doc-qa/tests/test_fix_cli.py -x` | Wave 0 |
| FIXR-03 | Lines inside tables are rejected | unit | `pytest gauss-doc-qa/tests/test_applier.py -x` | Wave 0 |
| FIXR-03 | Lines inside code blocks are rejected | unit | `pytest gauss-doc-qa/tests/test_applier.py -x` | Wave 0 |
| FIXR-03 | Lines inside directive arguments are rejected | unit | `pytest gauss-doc-qa/tests/test_applier.py -x` | Wave 0 |
| FIXR-04 | Sphinx build verification detects new warnings | unit | `pytest gauss-doc-qa/tests/test_verify.py -x` | Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m pytest gauss-doc-qa/tests/ -x -q`
- **Per wave merge:** `python -m pytest gauss-doc-qa/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `gauss-doc-qa/tests/test_resolver.py` -- covers FIXR-01 (fuzzy match resolution)
- [ ] `gauss-doc-qa/tests/test_applier.py` -- covers FIXR-01, FIXR-03 (fix application + safety)
- [ ] `gauss-doc-qa/tests/test_fix_cli.py` -- covers FIXR-02 (dry-run/apply CLI)
- [ ] `gauss-doc-qa/tests/test_verify.py` -- covers FIXR-04 (Sphinx build verification)
- [ ] `gauss-doc-qa/tests/fixtures/broken_refs.rst` -- test fixture with fixable and unfixable broken refs

## Open Questions

1. **What broken link patterns actually exist in the corpus?**
   - What we know: The links checker identifies broken `:func:`, `:doc:`, and `:ref:` references. The GAUSS domain does case-insensitive matching, so case mismatches resolve fine.
   - What's unclear: The actual distribution of broken link types (typos vs. genuinely missing functions vs. app module references). Running the checker against the real corpus would inform the fuzzy match threshold.
   - Recommendation: Run `gauss-qa check-refs --check links` against the real docs during plan execution to calibrate the resolver. Start with 0.85 threshold and adjust.

2. **Should :doc: and :ref: references also be auto-fixable?**
   - What we know: FIXR-01 says "broken internal links where target can be unambiguously determined." This could include `:doc:` references (file moved/renamed) and `:ref:` labels.
   - What's unclear: Whether `:doc:` fixes are common enough to warrant implementation in v1.
   - Recommendation: Start with `:func:` references only (the most common case in the GAUSS docs). Add `:doc:` resolution in a follow-up if needed. `:ref:` labels are too varied for fuzzy matching.

3. **How to handle the `auto_fixable` field on Finding?**
   - What we know: The field exists on Finding but is always False. The fixer needs findings marked as auto-fixable.
   - Recommendation: The fixer should accept any broken-link Finding and attempt resolution. Whether a fix is possible depends on the resolver output, not a pre-set flag. The `auto_fixable` field on Finding can remain informational.

## Sources

### Primary (HIGH confidence)
- Direct code inspection of `gauss-doc-qa/src/gauss_doc_qa/` -- models.py, checkers/links.py, checkers/seealso.py, cli.py, parser/sphinx_env.py
- Direct code inspection of `~/svn/gxmldoc/docs/util/GAUSSDomain.py` -- case-insensitive resolution via `_search_objects` using `casefold()`
- Direct inspection of RST files in `~/svn/gxmldoc/docs/` -- seealso patterns, reference patterns
- Python stdlib difflib documentation -- `get_close_matches()` API

### Secondary (MEDIUM confidence)
- RST whitespace sensitivity and table formatting rules -- well-known docutils behavior
- Pitfall 3 from `.planning/research/PITFALLS.md` -- auto-fix corruption risks

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all stdlib + existing project dependencies
- Architecture: HIGH - follows existing codebase patterns (checker model, CLI subcommands)
- Pitfalls: HIGH - well-documented RST corruption risks, mitigated by leaf-text-only + dry-run + verify
- Fix resolution strategy: MEDIUM - fuzzy matching approach is sound but threshold needs calibration against real corpus

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (stable domain, no fast-moving dependencies)

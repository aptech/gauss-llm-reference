# Phase 4: AI Persona Reviews - Research

**Researched:** 2026-03-14
**Domain:** Claude API integration for structured documentation reviews with persona-based rubrics
**Confidence:** HIGH

## Summary

Phase 4 adds three AI personas that review GAUSS documentation sections via the Claude API, producing structured binary findings that integrate into the existing Finding/report pipeline. The core technical challenge is not the API integration (straightforward with the Anthropic Python SDK) but rather designing rubrics tight enough to produce actionable findings without noise.

The existing codebase provides a clean integration path: the `Finding` dataclass, `BaseChecker` registry, and three report formatters (terminal/JSON/markdown) already handle everything downstream. The AI module needs to (1) define persona configs with binary rubrics, (2) submit doc sections to Claude with structured output schemas, and (3) convert responses into `Finding` objects. The Anthropic SDK's `messages.parse()` with Pydantic models is the cleanest approach for guaranteed schema compliance.

**Primary recommendation:** Use `anthropic` SDK with `messages.parse()` and Pydantic response models. Define exactly 5-8 binary pass/fail checks per persona. Each persona targets one doc type. Register a single `AIPersonaChecker` (or one per persona) in the checker registry so findings flow through the existing pipeline unchanged.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| AIRV-01 | Batch AI persona reviews via Claude API with structured binary rubrics (not free-text) | Anthropic SDK `messages.parse()` with Pydantic models guarantees structured output. Binary rubric design documented in Architecture Patterns section. |
| AIRV-02 | New GAUSS user persona reviews Getting Started content -- "Where did you get confused?" | Newcomer persona targets `getting-started/` docs (5 RST files). 6 binary checks focused on assumed knowledge, missing context, jargon. |
| AIRV-03 | Experienced developer persona reviews Command Reference spot-check -- "Is the signature, return type, and example correct?" | Expert persona targets `COMMAND_REF` pages. 7 binary checks on signature accuracy, return type, param docs, example correctness. |
| AIRV-04 | Technical writer persona reviews User Guide -- "Are concepts introduced before used? Undefined terms?" | Writer persona targets `user-guide/` docs. 6 binary checks on term introduction order, undefined jargon, prerequisite concepts. |
| AIRV-05 | Persona review findings integrate into the same Finding/report system as structural checks | AI checker produces `Finding` objects with same fields (file, line, severity, category, checker, message). No changes to report pipeline needed. |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| anthropic | >=0.80 | Claude API client | Official Anthropic Python SDK; `messages.parse()` returns typed Pydantic objects |
| pydantic | >=2.0 | Response schema models | SDK's `messages.parse()` accepts Pydantic BaseModel for structured output |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| click | >=8.3 (existing) | CLI subcommand for `gauss-qa review` | Already in project |
| rich | >=14.0 (existing) | Progress display during API calls | Already in project |
| pyyaml | >=6.0 | Persona config files | Only if using YAML configs; alternatively use Python dataclasses |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `messages.parse()` Pydantic | `messages.create()` + `output_config` JSON schema | Lower-level; parse() is simpler and type-safe |
| `messages.parse()` Pydantic | `tool_use` with strict mode | Overengineered; tool_use is for function calling, not response formatting |
| Anthropic Batch API | Sequential `messages.parse()` calls | Batch API has 50% cost savings but adds polling complexity; sequential is simpler for ~20-50 calls |
| YAML persona configs | Python dataclasses | YAML is more user-editable; dataclasses are simpler to test. Recommend dataclasses for v1 |

**Installation:**
```bash
pip install anthropic pydantic
```

Note: `pydantic` is likely already a transitive dependency of `anthropic`. Add `anthropic>=0.80` to `pyproject.toml` dependencies.

## Architecture Patterns

### Recommended Module Structure
```
gauss-doc-qa/src/gauss_doc_qa/
  ai/
    __init__.py
    personas.py        # Persona definitions (rubrics, system prompts, target doc types)
    schemas.py          # Pydantic response models for structured output
    reviewer.py         # Claude API submission + Finding conversion
    checker.py          # BaseChecker subclass(es) that wire into registry
```

### Pattern 1: Persona as Data, Not Code
**What:** Each persona is a data structure (dataclass or dict) containing: name, system prompt, target DocTypes, and a list of rubric checks. The reviewer module is generic -- it takes any persona config and runs it.
**When to use:** Always. Do not create separate code paths per persona.
**Example:**
```python
from dataclasses import dataclass, field
from gauss_doc_qa.models import DocType, Severity

@dataclass
class RubricCheck:
    id: str                    # e.g., "NEW-01"
    question: str              # Binary question: "Does X exist/match/..."
    fail_severity: Severity    # Severity if check fails
    category: str              # Finding category string

@dataclass
class Persona:
    name: str                  # "newcomer", "expert", "writer"
    description: str           # System prompt context
    target_doc_types: list[DocType]
    rubric: list[RubricCheck]
    model: str = "claude-sonnet-4-20250514"  # Cost-effective for rubric checks
```

### Pattern 2: Structured Output via Pydantic
**What:** Define response models that mirror the rubric. Each check gets a pass/fail boolean and an evidence string (the specific text that caused failure).
**Example:**
```python
from pydantic import BaseModel

class CheckResult(BaseModel):
    check_id: str
    passed: bool
    evidence: str       # Quote from doc or "" if passed
    line_hint: str      # Section/line where issue found, or ""

class PersonaReviewResponse(BaseModel):
    results: list[CheckResult]
```

### Pattern 3: Checker Registry Integration
**What:** Register AI persona checker(s) in the existing BaseChecker registry. Use a flag like `requires_api: bool = True` to distinguish from fast/sphinx checkers so the CLI can gate on it.
**Example:**
```python
class AIPersonaChecker(BaseChecker):
    name = "ai_personas"
    requires_sphinx = False
    requires_api = True       # New flag -- AI checkers need API key

    def check(self, parsed_doc: ParsedDoc, **kwargs) -> list[Finding]:
        persona_name = kwargs.get("persona")
        # ...submit to API, convert response to Findings
```

### Pattern 4: Doc Section Extraction
**What:** Before sending to Claude, extract the relevant section text from the ParsedDoc. Do not send entire RST files -- send the specific content the persona needs to evaluate.
**When to use:** Always. Reduces token cost and focuses the model.
**Details:**
- Newcomer persona: send full page content (Getting Started pages are short)
- Expert persona: send Format section + Examples section from Command Reference pages
- Writer persona: send full page content (User Guide pages need sequential reading)

### Anti-Patterns to Avoid
- **Free-text prompting:** Never ask Claude to "review this documentation." Always provide the binary rubric in the system prompt and require structured output.
- **Sending raw RST markup:** Strip directive syntax before sending. Claude should evaluate content, not markup. Convert to plain text or minimal markdown.
- **One API call per check:** Bundle all rubric checks for a persona into a single API call per document. The response model returns all check results at once.
- **Hardcoded prompts in code:** Keep system prompts as data (string constants or config), not buried in logic.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Structured API responses | Custom JSON parsing/validation | `anthropic` SDK `messages.parse()` + Pydantic | Guaranteed schema compliance, type safety, automatic retry on malformed output |
| Rate limiting | Custom sleep/retry loops | `anthropic` SDK built-in retries | SDK handles 429s, exponential backoff automatically |
| Progress display | Custom print statements | `rich.progress.Progress` | Already a dependency, handles terminal width, ETA |
| API key management | Custom env var loading | `anthropic.Anthropic()` default | SDK reads `ANTHROPIC_API_KEY` env var automatically |

## Common Pitfalls

### Pitfall 1: Noise from Open-Ended Prompts
**What goes wrong:** Prompts like "review for quality" produce subjective, unrepeatable findings. 60%+ of output is stylistic preference.
**Why it happens:** LLMs are trained to be helpful and verbose. Without constraints, they generate critique.
**How to avoid:** Every check must be binary (pass/fail) with a concrete, verifiable criterion. "Does the Format section contain a `.. function::` directive?" not "Is the Format section well-organized?"
**Warning signs:** If a check result can't be independently verified by reading the doc, the rubric is too loose.

### Pitfall 2: Token Cost Explosion
**What goes wrong:** Sending full RST files for 1,700 docs at ~2K tokens each = 3.4M input tokens per persona. With 3 personas = 10M+ tokens per run.
**Why it happens:** Not scoping which docs each persona reviews and not extracting relevant sections.
**How to avoid:**
- Newcomer: only `getting-started/` (5 files)
- Expert: sample of Command Reference pages (configurable N, default 20-50)
- Writer: only `user-guide/` (~8 files)
- Total: ~60-80 API calls max per full run
- Use claude-sonnet (not opus) for cost efficiency on binary rubric checks

### Pitfall 3: Conflating AI Findings with Structural Findings
**What goes wrong:** AI findings use different severity scales or categories, making merged reports confusing.
**How to avoid:** AI findings use the exact same `Finding` dataclass with `checker="ai_newcomer"` (or similar). Severity assigned by rubric config, not by Claude. Category strings follow existing conventions (lowercase_with_underscores).

### Pitfall 4: API Key Not Available Breaks CLI
**What goes wrong:** Importing the `ai` module at startup fails if `ANTHROPIC_API_KEY` is not set, breaking all CLI commands (even non-AI ones).
**How to avoid:** Lazy import pattern (same as Sphinx env). Only import `anthropic` inside the review command handler. If key is missing, raise a clear error message with instructions.

### Pitfall 5: Non-Deterministic Results
**What goes wrong:** Same doc produces different findings on repeated runs, making results hard to trust.
**How to avoid:** Use `temperature=0` for all rubric evaluation calls. Accept that some variation is inherent but binary checks are more stable than open-ended reviews.

## Code Examples

### Persona Definition
```python
# Source: project-specific design based on REQUIREMENTS.md
NEWCOMER_PERSONA = Persona(
    name="newcomer",
    description=(
        "You are a programmer learning GAUSS for the first time. "
        "You know Python and R but have never used GAUSS. "
        "Evaluate this Getting Started documentation page."
    ),
    target_doc_types=[DocType.GETTING_STARTED],
    rubric=[
        RubricCheck("NEW-01", "Does the page explain what GAUSS is before using it?", Severity.WARNING, "undefined_concept"),
        RubricCheck("NEW-02", "Are all GAUSS-specific terms (e.g., 'proc', 'retp', 'endp') explained on first use?", Severity.WARNING, "unexplained_term"),
        RubricCheck("NEW-03", "Does each code example show expected output or explain what it produces?", Severity.WARNING, "missing_output"),
        RubricCheck("NEW-04", "Are prerequisite steps (installation, file paths) mentioned before code that depends on them?", Severity.ERROR, "missing_prerequisite"),
        RubricCheck("NEW-05", "Can the examples be followed in order without skipping steps?", Severity.WARNING, "broken_sequence"),
        RubricCheck("NEW-06", "Are there any references to features not yet introduced at this point in the docs?", Severity.INFO, "forward_reference"),
    ],
    model="claude-sonnet-4-20250514",
)
```

### API Call with Structured Output
```python
# Source: Anthropic SDK docs (https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
import anthropic
from ai.schemas import PersonaReviewResponse

client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

response = client.messages.parse(
    model=persona.model,
    max_tokens=1024,
    temperature=0,
    system=persona.description + "\n\nEvaluate the document against each check. "
           "Return pass/fail with evidence for failures.",
    messages=[
        {"role": "user", "content": f"Document: {doc_text}\n\nRubric checks:\n{rubric_text}"}
    ],
    output_format=PersonaReviewResponse,
)

review = response.parsed_output
```

### Converting Results to Findings
```python
def review_to_findings(
    review: PersonaReviewResponse,
    persona: Persona,
    file_path: str,
) -> list[Finding]:
    findings = []
    rubric_map = {r.id: r for r in persona.rubric}
    for result in review.results:
        if not result.passed:
            check = rubric_map[result.check_id]
            findings.append(Finding(
                file=file_path,
                line=None,  # AI reviews typically can't pinpoint exact lines
                severity=check.fail_severity,
                category=check.category,
                checker=f"ai_{persona.name}",
                message=f"[{result.check_id}] {check.question} -- {result.evidence}",
            ))
    return findings
```

### CLI Integration
```python
@cli.command()
@click.option("--persona", type=click.Choice(["newcomer", "expert", "writer", "all"]),
              default="all", help="Which persona to run")
@click.option("--sample", type=int, default=20,
              help="Number of Command Reference pages to sample for expert persona")
@click.option("--format", "output_format", ...)
@click.pass_context
def review(ctx, persona, sample, output_format, output):
    """Run AI persona reviews on documentation."""
    # Lazy import
    from gauss_doc_qa.ai.reviewer import run_persona_review
    # ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Free-text AI doc reviews | Structured binary rubrics via `output_config` or `messages.parse()` | Anthropic structured outputs, late 2025 | Eliminates parsing ambiguity, guarantees schema |
| `tool_use` for structured output | `messages.parse()` with Pydantic | Anthropic SDK 0.80+, 2026 | Simpler API, built-in validation |
| Manual JSON schema definition | Pydantic model auto-conversion | Same | Less boilerplate, type safety |

**Model recommendation for rubric checks:** `claude-sonnet-4-20250514` -- fast, cost-effective, sufficient for binary pass/fail evaluation. Save Opus for complex reasoning tasks. Haiku would work too for simple rubrics but may miss nuance in "is this example correct?" checks.

## Open Questions

1. **Command Reference sampling strategy**
   - What we know: Expert persona should spot-check Command Reference pages, not review all ~1,400
   - What's unclear: Random sample? Most-linked pages? User-specified list?
   - Recommendation: Default to random sample of 20 pages. Allow `--pages` flag for user-specified list. Consider using cross-ref frequency ranking from Phase 2 to prioritize high-traffic pages.

2. **RST-to-text conversion depth**
   - What we know: Should not send raw RST directives to Claude
   - What's unclear: How much RST structure to preserve vs strip
   - Recommendation: Convert RST to plain text by extracting text nodes from docutils AST. Preserve section headings. Strip directive markers, field lists become plain text.

3. **Anthropic Batch API vs sequential**
   - What we know: Batch API offers 50% cost savings but requires polling
   - What's unclear: Whether the ~60-80 call volume justifies batch complexity
   - Recommendation: Start with sequential calls + progress bar. Add batch mode as optimization later if cost is a concern.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.0+ |
| Config file | None (uses pyproject.toml or pytest defaults) |
| Quick run command | `pytest gauss-doc-qa/tests/ -x -q` |
| Full suite command | `pytest gauss-doc-qa/tests/ -v` |

### Phase Requirements to Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AIRV-01 | Structured binary rubrics produce valid Findings | unit | `pytest gauss-doc-qa/tests/test_reviewer.py -x` | No -- Wave 0 |
| AIRV-02 | Newcomer persona checks Getting Started content | unit (mocked API) | `pytest gauss-doc-qa/tests/test_personas.py::test_newcomer -x` | No -- Wave 0 |
| AIRV-03 | Expert persona checks Command Reference pages | unit (mocked API) | `pytest gauss-doc-qa/tests/test_personas.py::test_expert -x` | No -- Wave 0 |
| AIRV-04 | Writer persona checks User Guide pages | unit (mocked API) | `pytest gauss-doc-qa/tests/test_personas.py::test_writer -x` | No -- Wave 0 |
| AIRV-05 | AI findings integrate into existing report pipeline | unit | `pytest gauss-doc-qa/tests/test_ai_integration.py -x` | No -- Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest gauss-doc-qa/tests/ -x -q`
- **Per wave merge:** `pytest gauss-doc-qa/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `gauss-doc-qa/tests/test_reviewer.py` -- covers AIRV-01 (API call mocking, response-to-Finding conversion)
- [ ] `gauss-doc-qa/tests/test_personas.py` -- covers AIRV-02, AIRV-03, AIRV-04 (persona configs, rubric validation)
- [ ] `gauss-doc-qa/tests/test_ai_integration.py` -- covers AIRV-05 (AI findings in report pipeline)
- [ ] `gauss-doc-qa/tests/fixtures/getting_started_sample.rst` -- sample Getting Started RST for newcomer tests
- [ ] `gauss-doc-qa/tests/fixtures/command_ref_sample.rst` -- sample Command Reference RST for expert tests
- [ ] `gauss-doc-qa/tests/fixtures/user_guide_sample.rst` -- sample User Guide RST for writer tests
- [ ] Add `anthropic>=0.80` and `pydantic>=2.0` to pyproject.toml dependencies

## Sources

### Primary (HIGH confidence)
- [Anthropic Structured Outputs docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs) -- `messages.parse()` API, Pydantic integration, JSON schema approach
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python) -- v0.84.0, batch API, retry behavior
- Project codebase: `models.py`, `checkers/base.py`, `cli.py`, `report/terminal.py` -- existing patterns for Finding, BaseChecker, CLI wiring

### Secondary (MEDIUM confidence)
- [DeepWiki Anthropic SDK batch processing](https://deepwiki.com/anthropics/anthropic-sdk-python/5.5-message-batches) -- Batch API structure and lifecycle
- Project research docs: `PITFALLS.md` Pitfall 4 (AI review noise), `ARCHITECTURE.md` (AI Persona Runner design), `FEATURES.md` (persona review feature spec)

### Tertiary (LOW confidence)
- Model pricing and token limits for claude-sonnet-4 vs haiku -- based on training data, may have changed. Verify before committing to model choice.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- Anthropic SDK docs verified, `messages.parse()` API confirmed via official docs
- Architecture: HIGH -- builds on established project patterns (BaseChecker, Finding, CLI), no novel architecture needed
- Pitfalls: HIGH -- noise prevention via binary rubrics is well-documented in project research and industry practice
- API integration: MEDIUM -- exact `messages.parse()` parameter names verified but SDK version compatibility not tested locally

**Research date:** 2026-03-14
**Valid until:** 2026-04-14 (Anthropic SDK is actively developed; check for API changes)

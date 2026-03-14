# Research Summary: GAUSS Documentation QA System

**Domain:** Documentation QA automation for Sphinx RST sources
**Researched:** 2026-03-14
**Overall confidence:** HIGH

## Executive Summary

The GAUSS documentation corpus consists of ~1,716 RST files in a Sphinx project with a custom GAUSS domain, custom roles, and a custom HTML translator. The most important architectural discovery is that cross-reference resolution cannot be done independently of Sphinx -- the custom `GAUSSDomain.py` registers function directives and reference roles that standard docutils cannot resolve. This means the system needs two parsing modes: fast docutils-only parsing for structural checks, and a slower Sphinx environment load for cross-reference and toctree analysis.

The recommended stack is pure Python with docutils 0.22.4, Sphinx 9.1.0, the anthropic SDK for AI reviews, rapidfuzz for terminology matching, and click/rich for CLI and reporting. All core dependencies are already installed on the system. No external services are needed beyond the Anthropic API for persona reviews and deep validation.

The feature landscape divides cleanly into three tiers: structural checks (docutils-based, fast, zero API cost), AI persona reviews (Claude API, qualitative), and deep function validation (Claude API, targeted at top-N functions by cross-reference frequency). The tiers are independent and can be built incrementally.

The most dangerous pitfalls are: (1) using regex instead of docutils for RST parsing, which produces false positives on 20% of files; (2) ignoring the custom GAUSS domain when validating cross-references, which would make the entire link-checking tier unreliable; and (3) auto-fix scripts that corrupt RST whitespace-sensitive formatting. All three are preventable with the right architectural choices in Phase 1.

## Key Findings

**Stack:** Python 3.14 + docutils 0.22.4 + Sphinx 9.1.0 + anthropic SDK + rapidfuzz + click/rich. All verified current, all already installed.

**Architecture:** Two-engine parsing (docutils for speed, Sphinx for cross-refs) feeding a three-tier check pipeline with uniform Finding objects.

**Critical pitfall:** The custom GAUSS Sphinx domain (`GAUSSDomain.py`, `GAUSSRoles.py`) must be loaded for any cross-reference validation. The `default_role='any'` setting means bare backtick references also resolve through this domain.

## Implications for Roadmap

Based on research, suggested phase structure:

1. **Foundation + Fast Structural Checks** - Build the parsing layer (docutils), doc type classifier, Finding model, CLI skeleton, and fast checks (code blocks, section structure, signature completeness). Zero external dependencies. Immediate value.
   - Addresses: code block presence, section validation, signature completeness, report generation
   - Avoids: Pitfall 1 (regex parsing), Pitfall 11 (wrong template assumptions), Pitfall 13 (missing literal blocks)

2. **Sphinx-Based Cross-Reference Checks** - Load the Sphinx environment with the GAUSS domain. Build link validator, orphan detector, and cross-reference frequency counter.
   - Addresses: broken link detection, orphan pages, top-N function ranking
   - Avoids: Pitfall 2 (ignoring custom domain), Pitfall 6 (naive orphan detection)

3. **Terminology + Auto-Fix** - Build glossary enforcement with rapidfuzz and conservative auto-fix for safe issues.
   - Addresses: terminology consistency, auto-fix for fixable issues
   - Avoids: Pitfall 3 (RST corruption), Pitfall 7 (aggressive glossary)

4. **AI Persona Reviews** - Build batch Claude API integration with structured prompts and binary rubrics per persona.
   - Addresses: qualitative doc review across 4 personas x 4 sections
   - Avoids: Pitfall 4 (noisy AI output)

5. **Deep Validation** - Use top-N function list from Phase 2 to run comprehensive AI-assisted validation on highest-impact function pages.
   - Addresses: correctness validation, not just structural completeness
   - Avoids: Pitfall 5 (structure without correctness), Pitfall 8 (frequency-only ranking)

**Phase ordering rationale:**
- Phase 1 before 2: docutils parsing is the foundation everything builds on. Getting it right prevents cascading issues.
- Phase 2 before 3: cross-reference resolution must work before auto-fix can propose corrections for broken links.
- Phase 3 before 4: automated checks should establish a baseline before spending API budget on AI reviews.
- Phase 4 before 5: persona review infrastructure (API integration, structured output, rate limiting) is reused by deep validation.
- Each phase delivers standalone value. No phase is blocked on a future phase.

**Research flags for phases:**
- Phase 2: Needs validation that Sphinx 9.1.0's Python API works correctly with the custom GAUSS domain. Test early.
- Phase 4: Prompt engineering for persona rubrics will require iteration. Budget time for prompt tuning.
- Phase 5: The cross-reference frequency ranking should be supplemented with domain expertise to avoid utility-function bias.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified via pip index. All already installed on the system |
| Features | HIGH | Feature landscape derived from direct corpus inspection and PROJECT.md requirements |
| Architecture | HIGH | Two-engine approach (docutils + Sphinx) is well-motivated by the custom domain. Data structures are straightforward |
| Pitfalls | HIGH for structural, MEDIUM for AI | Structural pitfalls verified against actual corpus. AI review pitfalls based on training data patterns |
| Sphinx 9.x API | MEDIUM | Could not verify Sphinx 9.x specific API changes (WebSearch unavailable). Core constructor is stable but test early |

## Gaps to Address

- **Sphinx 9.x Python API compatibility:** Need to verify that `sphinx.application.Sphinx` with a dummy builder works correctly for environment loading. Test against the actual GAUSS docs early in Phase 2.
- **Custom GAUSS domain completeness:** `GAUSSDomain.py` should be fully read to understand all registered roles, directives, and index types before building the link validator.
- **Exclude patterns in conf.py:** The conf.py has explicit `exclude_patterns` for dbnomics and fred files. The inventory scanner must respect these.
- **App module subdirectories:** The docs have ~12 subdirectories for application modules (tsmt, fanpac, cmlmt, etc.). Need to verify whether these follow the same Command Reference template or have their own conventions.
- **AI review cost estimation:** Need to estimate token usage for ~16 persona reviews + ~20 deep validations to budget API spend.

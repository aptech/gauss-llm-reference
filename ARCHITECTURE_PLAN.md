# GAUSS LLM Reference Architecture

Status: current ownership and routing record.

Last verified: 2026-07-15.

## Purpose

This repository maintains concise, reviewable GAUSS reference material for AI
assistants and a separate Python tool for auditing GAUSS documentation. It does
not generate client-specific copies of the reference and does not currently run
a YAML, embeddings, RAG, or MCP build pipeline.

The former 420-line source/build/embeddings/MCP migration proposal is a
historical design at commit `2358ca2`. It was never the tracked repository
layout and is not an executable roadmap. Any future retrieval architecture
requires a new, explicitly approved plan based on the repository state at that
time.

## Current Layout

```text
gauss-llm-reference/
├── README.md                  # canonical general GAUSS quick reference
├── AGENTS.md                  # thin Codex-compatible routing entrypoint
├── CLAUDE.md                  # thin Claude-compatible routing entrypoint
├── language/                  # detailed language and library topics
├── gotchas/                   # focused failure modes and corrections
├── vs-other-languages/        # translation guidance
├── apps/                      # application-module references
├── gauss-doc-qa/              # executable Python documentation-audit tool
└── .planning/                 # historical gauss-doc-qa delivery record
```

There are no tracked `.Codex/gauss/` or `.claude/gauss/` topic trees. Client
entrypoints route to the paths above.

## Content Ownership

| Content | Owner |
|---|---|
| General GAUSS rules and quick reference | `README.md` |
| Detailed language behavior | the relevant file in `language/` |
| Focused mistakes and corrections | the relevant file in `gotchas/` |
| Cross-language translation | the relevant file in `vs-other-languages/` |
| Application-module behavior | the relevant file in `apps/` |
| Client discovery and routing | byte-identical `AGENTS.md` and `CLAUDE.md` |
| Documentation-audit implementation | `gauss-doc-qa/` |
| Completed QA-tool delivery provenance | `.planning/` |

The same substantive rule should not be maintained in both client entrypoints.
When a general rule needs more detail, keep the compact rule in `README.md` and
put the expansion in one topic file with an explicit link.

## Reference And QA-Tool Boundary

The root reference tree teaches assistants how to write GAUSS. `gauss-doc-qa/`
is Python software that checks a documentation corpus. A completed QA-tool
milestone does not change the status of the root reference architecture, and a
reference-content edit does not reopen the archived QA-tool delivery plan.

Executable changes under `gauss-doc-qa/` follow its `pyproject.toml` and test
suite. Routing-only Markdown changes use path/link and whitespace checks.

## Change Rules

1. Keep `AGENTS.md` and `CLAUDE.md` byte-identical and limited to routing,
   ownership, and validation guidance.
2. Do not add hidden client-specific copies of `language/` or `apps/`.
3. Preserve the unique general reference when reducing context; move it to its
   declared owner before shrinking an entrypoint.
4. Treat `.planning/` as immutable historical provenance unless correcting a
   factual error in that history.
5. Add generated outputs, embeddings, an MCP server, or a new source schema
   only through a separately reviewed architecture plan with explicit owners,
   validation, and regeneration rules.

## Validation

For architecture or routing changes:

- confirm every referenced repository path exists;
- confirm `AGENTS.md` and `CLAUDE.md` remain byte-identical;
- confirm no live route targets `.Codex/gauss/` or `.claude/gauss/`;
- confirm historical phase records were not rewritten; and
- run `git diff --check` on the bounded packet.

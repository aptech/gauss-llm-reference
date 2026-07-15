# Agent Instructions

This repository has two distinct surfaces: GAUSS reference content at the
root and an executable Python documentation-audit tool under `gauss-doc-qa/`.
Keep their instructions, plans, and status separate.

## Reference routing

- For GAUSS code generation or review, read [README.md](README.md), then load
  only the relevant files under `language/`, `gotchas/`,
  `vs-other-languages/`, or `apps/`.
- Remote or single-file consumers should fetch the
  [canonical GitHub reference](https://github.com/aptech/gauss-llm-reference/blob/main/README.md).
- `README.md` is the single general GAUSS quick reference. Topic files own
  detailed subject guidance. Do not duplicate either body in this entrypoint.
- Do not route to `.Codex/gauss/` or `.claude/gauss/`; those paths do not exist
  in this repository.

## Repository boundaries

- Changes to `gauss-doc-qa/` follow its Python project configuration and tests.
- `.planning/` is a non-executable historical record of completed
  `gauss-doc-qa` milestones. Do not resume it, auto-chain it, or treat its phase
  files as current agent instructions.
- `AGENTS.md` and `CLAUDE.md` are intentional client mirrors. Keep them
  byte-identical and small; substantive reference content belongs elsewhere.
- Preserve dated research, validation, verification, and milestone records
  unless the task explicitly concerns historical correction.

## Validation

- For routing-only Markdown changes, verify referenced repository paths and
  run whitespace checks.
- If executable Python or its tests change, run the focused `gauss-doc-qa`
  test targets required by that change.

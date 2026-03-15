---
phase: 4
slug: ai-persona-reviews
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | gauss-doc-qa/pyproject.toml |
| **Quick run command** | `cd gauss-doc-qa && python -m pytest tests/ -x -q` |
| **Full suite command** | `cd gauss-doc-qa && python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd gauss-doc-qa && python -m pytest tests/ -x -q`
- **After every plan wave:** Run `cd gauss-doc-qa && python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | AIRV-01 | unit | `pytest tests/test_persona_models.py` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | AIRV-02, AIRV-03, AIRV-04 | unit | `pytest tests/test_persona_checkers.py` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | AIRV-05 | integration | `pytest tests/test_persona_cli.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_persona_models.py` — stubs for rubric models and API client
- [ ] `tests/test_persona_checkers.py` — stubs for persona checkers with mocked API
- [ ] `tests/test_persona_cli.py` — stubs for CLI review subcommand

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| API key handling | AIRV-01 | Requires real ANTHROPIC_API_KEY | Set key, run `gauss-qa review --persona newcomer --docs-dir ~/svn/gxmldoc/docs/getting-started/` |
| Review quality | AIRV-02/03/04 | Requires human judgment on finding relevance | Run each persona against real docs, assess signal-to-noise ratio |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

---
phase: 3
slug: auto-fix
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 3 — Validation Strategy

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
| 03-01-01 | 01 | 1 | FIXR-01 | unit | `pytest tests/test_resolver.py` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | FIXR-02, FIXR-03 | unit | `pytest tests/test_applier.py` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | FIXR-04 | integration | `pytest tests/test_verify.py` | ❌ W0 | ⬜ pending |
| 03-02-02 | 02 | 2 | FIXR-01 | integration | `pytest tests/test_cli.py -k fix` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_resolver.py` — stubs for fuzzy match resolution
- [ ] `tests/test_applier.py` — stubs for safe RST line editing
- [ ] `tests/test_verify.py` — stubs for Sphinx build verification
- [ ] Test fixtures with broken refs to fix

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Dry-run output readability | FIXR-01 | Visual formatting check | Run `gauss-qa fix --docs-dir ~/svn/gxmldoc/docs/ --dry-run`, verify diff-like output |
| No RST corruption on real docs | FIXR-03 | Needs real corpus | Apply fix, run `sphinx-build`, compare error count |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

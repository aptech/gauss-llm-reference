---
phase: 2
slug: cross-reference-validation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-14
---

# Phase 2 — Validation Strategy

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
| 02-01-01 | 01 | 1 | FOUN-02 | integration | `pytest tests/test_sphinx_env.py` | ❌ W0 | ⬜ pending |
| 02-01-02 | 01 | 1 | STRC-03 | integration | `pytest tests/test_xref_checker.py` | ❌ W0 | ⬜ pending |
| 02-02-01 | 02 | 2 | STRC-04 | integration | `pytest tests/test_orphan_checker.py` | ❌ W0 | ⬜ pending |
| 02-02-02 | 02 | 2 | STRC-07 | integration | `pytest tests/test_coverage_checker.py` | ❌ W0 | ⬜ pending |
| 02-02-03 | 02 | 2 | STRC-08 | integration | `pytest tests/test_seealso_checker.py` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_sphinx_env.py` — stubs for Sphinx environment loading
- [ ] `tests/test_xref_checker.py` — stubs for cross-reference validation
- [ ] `tests/test_orphan_checker.py` — stubs for orphan page detection
- [ ] `tests/test_coverage_checker.py` — stubs for function coverage analysis
- [ ] `tests/test_seealso_checker.py` — stubs for See Also link validation

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Sphinx dummy build on real docs | FOUN-02 | Requires full GAUSS docs corpus + Sphinx theme | Run `gauss-qa scan --docs-dir ~/svn/gxmldoc/docs/ --check xref` |
| Orphan detection accuracy | STRC-04 | Need to verify against known toctree structure | Compare orphan list against manual toctree walk |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

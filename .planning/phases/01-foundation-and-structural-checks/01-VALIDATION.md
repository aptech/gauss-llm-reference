---
phase: 1
slug: foundation-and-structural-checks
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-14
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `python -m pytest tests/ -x -q` |
| **Full suite command** | `python -m pytest tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/ -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01 | 1 | FOUN-01 | unit | `pytest tests/test_parser.py` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01 | 1 | FOUN-03 | unit | `pytest tests/test_finding.py` | ❌ W0 | ⬜ pending |
| 01-02-01 | 02 | 1 | STRC-01 | integration | `pytest tests/test_checks.py -k code_block` | ❌ W0 | ⬜ pending |
| 01-02-02 | 02 | 1 | STRC-02 | integration | `pytest tests/test_checks.py -k empty_block` | ❌ W0 | ⬜ pending |
| 01-02-03 | 02 | 1 | STRC-05 | integration | `pytest tests/test_checks.py -k section` | ❌ W0 | ⬜ pending |
| 01-02-04 | 02 | 1 | STRC-06 | integration | `pytest tests/test_checks.py -k signature` | ❌ W0 | ⬜ pending |
| 01-03-01 | 03 | 2 | FOUN-04 | integration | `pytest tests/test_cli.py` | ❌ W0 | ⬜ pending |
| 01-03-02 | 03 | 2 | REPT-01 | integration | `pytest tests/test_report.py -k terminal` | ❌ W0 | ⬜ pending |
| 01-03-03 | 03 | 2 | REPT-02 | integration | `pytest tests/test_report.py -k json` | ❌ W0 | ⬜ pending |
| 01-03-04 | 03 | 2 | REPT-03 | integration | `pytest tests/test_report.py -k markdown` | ❌ W0 | ⬜ pending |
| 01-03-05 | 03 | 2 | REPT-04 | integration | `pytest tests/test_report.py -k summary` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/conftest.py` — shared fixtures (sample RST content strings)
- [ ] `tests/test_parser.py` — stubs for RST parsing and doc type classification
- [ ] `tests/test_finding.py` — stubs for Finding dataclass
- [ ] `tests/test_checks.py` — stubs for structural checks
- [ ] `tests/test_cli.py` — stubs for CLI entry point
- [ ] `tests/test_report.py` — stubs for report formatters

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Terminal color output readable | REPT-01 | Color rendering depends on terminal | Run CLI, visually confirm ERROR=red, WARNING=yellow, INFO=blue |
| Report against real GAUSS docs | All STRC-* | Integration with ~1,700 RST files | Run `gaussdocqa scan ~/svn/gxmldoc/docs/`, verify findings are reasonable |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending

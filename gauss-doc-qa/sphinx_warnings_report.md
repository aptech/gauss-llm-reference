# Sphinx Build Warnings Report

Generated 2026-03-20 from `sphinx-build` (dummy builder) on ~/svn/gxmldoc/docs/
Sphinx 8.2.3, Python 3.11, 1,755 documents processed.

**Total warnings: 1,220**

## Summary

| Category | Count | Actionable? |
|----------|-------|-------------|
| Ambiguous cross-references (`default_role='any'`) | ~500 | LOW — backtick words matching both doc pages and labels |
| Unresolved `any` references | 363 | LOW — bare backtick words like `ssModel`, `vector`, `0`, `1`, `HDF5` that aren't functions |
| RST formatting issues | ~100 | MEDIUM — missing blank lines, bad emphasis, short underlines |
| Unreadable images | 71 | MEDIUM — mostly TSMT orphan pages (already identified) |
| **Orphan pages** | **68** | **HIGH — pages not in any toctree** |

## Orphan Pages (68)

Pages that exist on disk but are not linked from any toctree. Users cannot navigate to these.

### Theme files (ignore — 3 pages)
- `_themes/sphinx_rtd_theme/tests/roots/*/index.rst`

### Main docs (6 pages — likely should be in toctree)
- `contingency.rst` — contingency table function
- `dfcontrolcreate.rst` — dataframe control struct create
- `equal.rst` — equality operator
- `fglscontrolcreate.rst` — FGLS control struct create
- `hacse.rst` — HAC standard errors
- `kmeanscontrolcreate.rst` — k-means control struct create
- `machine-learning.rst` — ML landing page
- `not-equal.rst` — inequality operator
- `plotsetxticlabelfont.rst` — plot tick label font
- `plotsetyticlabelfont.rst` — plot tick label font
- `cmlmtinversewaldlimits.rst` — CML inverse Wald limits

### App module orphans (likely need toctree entries)
- `cmlmt/` — 4 pages (cml_vs_cmlmt, cmlmt-ug-inference, cmlmtcontrolcreate, ml-bayes-limits-example)
- `sslib/` — 4 pages (example-one-time-invariant, sslib-landing, template-full, template-post-estimation)
- `tsmt/` — 27 pages (various VAR, time series functions)
- `mlmt/` — 1 page (mlmtcontrolcreate)
- `optmt/` — 1 page (opmtcontrolcreate)

### Other
- `bet/include/dgpout.rst` — include fragment (correct to be orphan)
- `plot-gallery/` — 2 pages (plant-production-bars, unemp-mtg30)
- `timeseries/index.rst` — time series landing page
- `index.rst` — main index (Sphinx sometimes flags this)
- `dbnomics_search.rst` — DB.nomics function

## Ambiguous Cross-References (~500)

These are caused by `default_role='any'` in conf.py. When a word in backticks matches both a document name AND a label/function, Sphinx warns. Top offenders:

| Word | Occurrences | Conflict |
|------|-------------|----------|
| `trap` | 65 | doc page vs label |
| `open` | 34 | doc page vs label |
| `save` | 26 | doc page vs label |
| `print` | 26 | doc page vs label |
| `gosub` | 19 | doc page vs label |
| `end` | 19 | doc page vs label |
| `proc` | 15 | doc page vs label |
| `new` | 15 | doc page vs label |

**Fix:** Change backtick references to explicit `:func:\`trap\`` or `:doc:\`trap\`` roles to disambiguate. This is a bulk fix across many pages.

## Unresolved `any` References (363)

Bare backtick words that Sphinx cannot resolve to any target. NOT broken `:func:` references. Top offenders:

| Word | Count | What it is |
|------|-------|-----------|
| `ssModel` | 8 | Structure name (not a function) |
| `1` / `0` | 16 | Literal numbers in backticks |
| `modelProc` | 7 | Procedure type reference |
| `vector` | 6 | Type description |
| `extern` | 6 | Language keyword |
| `push` | 5 | Language keyword |
| `HDF5` / `CSV` / `C` | 13 | File format names |
| `formula string` | 13 | Concept reference |

**Fix:** Replace backticks with double backticks (````code````) for code-styled text that isn't a cross-reference, or use `:ref:` for concept links.

## RST Formatting (100)

| Issue | Count |
|-------|-------|
| Blank line required after table | 31 |
| Literal block expected; none found | 26 |
| Line block ends without blank line | 26 |
| Inline emphasis start-string without end-string | 26 |
| Title underline too short | 20 |

These are minor RST hygiene issues. They may affect rendering quality.

## Recommendations

1. **Add orphan main-docs pages to toctrees** — 11 pages (contingency, dfcontrolcreate, equal, etc.) should be findable
2. **Disambiguate top cross-references** — fix `trap`, `open`, `print` backtick references (high volume, ~150 warnings)
3. **Fix RST formatting** — blank lines after tables, literal block markers (100 warnings)
4. **Leave app module orphans** — these are likely superseded TSMT pages, same as the equation SVGs

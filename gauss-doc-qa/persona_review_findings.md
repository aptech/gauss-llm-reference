# Persona Review Findings — Top 300 Command Reference Pages

Generated 2026-03-15 from open-ended confusion review across 4 personas.
Reviewed by two skeptical experienced GAUSS users. Verdicts noted.

## Critical Bugs (all verified CORRECT by reviewers)

| File | Bug | Status |
|------|-----|--------|
| stdc.rst | Formula shows `s * (n-1)/n` but should be `s * sqrt((n-1)/n)` | FIXED |
| cdfmvte.rst | Param `x` described as "Lower limits" but it's upper limits | FIXED |
| sqpsolve.rst | `_sqp_IneqProc` says "equality" should be "inequality"; `p[1]*[2]` missing `p` | FIXED |
| dttoutc.rst | Remarks say "July 15" but number shows 0703 (July 3) | FIXED |
| scalmiss.rst | Example `s = s +s umc(y)` should be `s = s + sumc(y)` | FIXED |
| intsimp.rst | Example uses `xl` but variable is named `xlims` | FIXED |
| chol.rst | Trap table shows trap 1 "terminate" — should return error code 10 | FIXED |
| polymake.rst | Shows `11^x` should be `11x` | FIXED |
| scalerr.rst | Example uses `x` without defining it | FIXED |
| plotsave.rst | Default units contradicts (px vs cm); example .png vs described .pdf | FIXED |
| plotcanvassize.rst | Remarks call it `plotSetCanvas` (wrong name) | FIXED |
| glm.rst | Section says "SAS sas7bdat" but loads detroit.dta (Stata) | FIXED |
| getHeaders.rst | Same SAS/Stata mislabel | FIXED |
| dtdayofweek.rst | Comment says "Get quarters" (copy-paste from another page) | FIXED |
| dtdayofyear.rst | Comment says "Print years" but prints day of year | FIXED |
| h5read.rst | Comment says "4 rows 3 cols" but code sets r=3; c=2 | FIXED |
| strindx.rst | Example calls `strrindx` (wrong function) | FIXED |
| timeDiffDT.rst | Return type says "Scalar" but returns NxK; comment says "18 months" but computes minutes | FIXED |
| dataopen.rst | Remarks contain `glm(...)` copy-paste from another page | FIXED |
| inthp2/3/4.rst | All reference `inthp1` in DS description (copy-paste) | FIXED |
| lapgeig.rst | seealso references itself | FIXED |
| getorders.rst | Stray "sss" in Purpose | FIXED |
| cdfbinomialinv.rst | Missing semicolon in example | FIXED |

Previously fixed (commits a2a90a40, e5d5c897):
- pdfcauchy.rst `:rtypep:` typo, seqaseqm.rst missing 256, loadd.rst SAS mislabel,
  pdfweibull.rst incomplete type, bessely.rst undefined `n`, fglscontrolcreate.rst copy-paste,
  knnclassify.rst param mismatch, movingaveexpwgt.rst impossible inequality, pacf.rst missing arg,
  pdftruncnorm.rst lower/upper swap, recservar.rst AR(2)/VAR(1), resetsourcepaths.rst false return,
  ridgecpredict.rst :return vs :param, toeplitz.rst wrong output, trigamma.rst rewrite

## Validated Confusion Points (reviewers agree these are real)

These are not bugs but genuine traps worth documenting:

| Issue | What to do |
|-------|-----------|
| `stof("")` returns 0, not missing | Add warning note — silent data corruption risk for empty strings |
| `strtof "1.2 1.9"` silently becomes complex | Add warning note — wrong results with no error for space-separated numbers |
| `reclassifyCuts`: `close_right=1` makes right side OPEN | Add clarifying note — parameter name is opposite of behavior |
| `momentd` adds constant column via `__con=1` global | Add prominent note — function silently changes output dimensions |
| `unique` flattens matrices to unique elements | Add remark: "operates element-wise, not unique rows" |
| `rndCreateState` Sobol overload: 2nd param is dimension not seed | Add clear note on the Sobol/Niederreiter case |
| ~15 pages say "SAS dataset" but load .dta (Stata) | Batch fix section headers |
| `trap` mechanism needs cross-references | Add brief explanation or link on each page that mentions trap |
| `recserar`: signature uses `rho`, Remarks use `a` | Fix param name consistency |
| `setcollabels`: parameter descriptions appear swapped | Verify against implementation and fix |
| `log()` computes base-10, not ln | Already fixed — added remark pointing to `ln()` |
| `plotScatter` Example 2: axis labels contradict column order | Fix the example |
| `olsqr` example uses exact system (0 df) | Replace with overdetermined example |
| `cdftnc`: `nonc` is sqrt of noncentrality parameter | Add clarifying note |

## Rejected / Overstated (reviewers say these are NOT problems)

GAUSS has its own conventions. These are not documentation bugs:

| Claim | Why it's fine |
|-------|---------------|
| `sumc` returns Kx1 column vector | Fundamental GAUSS convention — `c` suffix = column-wise |
| `minc` not like R's `min()` | Same convention, users learn this on day one |
| `delif` removes TRUE rows (opposite of R) | "Delete if" is clear English. `selif` keeps TRUE rows. The pair is self-explanatory |
| `dummy` does binning not indicators | Purpose line is clear. GAUSS ≠ R/Stata |
| `contains` returns scalar not element-wise | Return type is documented |
| `ols` residuals off by default | Documented behavior. Use `olsmt` for modern code |
| `ethsec` hundredths of a second | Standard unit, documented |
| `datestr` 2-digit year | Standard format, users know what they're getting |
| FFT 1/N scaling differs from MATLAB | Documented in Remarks. Every FFT library differs |
| `error(0)` equals missing value | By design, well-understood by experienced users |
| GML library needs paid-package note | Website covers licensing, not per-function-page responsibility |
| DT vs POSIX date format differences | Each system documented on its own pages |
| `substute` function name misspelling | Historical name since 1990s — cannot change without breaking code |
| `intgrat2/3` upper limit first | GAUSS convention, documented on the page |
| `recserar` signature/Remarks use different names | Standard GAUSS doc practice (Reviewer #1 says OVERSTATED; keeping as valid per Reviewer #2) |

## Fixes Applied — Unnecessary (reviewer feedback)

Two fixes from the binary review were flagged as unnecessary:
- `between.rst` case change (`x` → `X`) — GAUSS is case-insensitive
- `annotationsetlinepen.rst` `&` prefix — convention is `&` only in signature line, not `:param:` directive

These are cosmetic and do no harm, but weren't needed.

## Examples Added — All Verified

30 of ~200 added examples were spot-checked by Reviewer #2. All 30 rated GOOD:
correct GAUSS code, verified output, appropriate scope. Zero incorrect, zero misleading.

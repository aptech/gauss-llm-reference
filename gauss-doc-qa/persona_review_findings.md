# Persona Review Findings — Top 300 Command Reference Pages

Generated 2026-03-15 from open-ended confusion review across 4 personas.

## Critical Bugs (factual errors that mislead users)

| File | Bug | Severity |
|------|-----|----------|
| stdc.rst | Formula shows `s * (n-1)/n` but should be `s * sqrt((n-1)/n)` | HIGH — wrong math |
| cdfmvte.rst | Param `x` described as "Lower limits" but it's upper limits | HIGH — inverted meaning |
| sqpsolve.rst | `_sqp_IneqProc` says "equality" should be "inequality"; example has `p[1]*[2]` missing `p` | HIGH — won't run |
| dttoutc.rst | Remarks say "July 15" but number shows 0703 (July 3) | HIGH — wrong date |
| scalmiss.rst | Example has `s = s +s umc(y)` should be `s = s + sumc(y)` | HIGH — won't run |
| intsimp.rst | Example uses `xl` but variable is named `xlims` | HIGH — won't run |
| chol.rst | Trap table shows trap 0 and trap 1 both "terminate" — trap 1 should return error code | HIGH — wrong behavior |
| polymake.rst | Shows `11^x` should be `11x` (i.e. `11*x`) | MEDIUM — wrong math |
| scalerr.rst | Example uses `x` without defining it | MEDIUM — won't run |
| plotsave.rst | Default units says "px" in one place, "cm" in another; example .png vs described .pdf | MEDIUM — contradictory |
| plotcanvassize.rst | Remarks call function `plotSetCanvas` (wrong name, actual is `plotCanvasSize`) | MEDIUM |
| glm.rst | Section header says "SAS sas7bdat" but loads `detroit.dta` (Stata) | MEDIUM — misleading |
| getHeaders.rst | Same "SAS dataset" mislabel with detroit.dta | MEDIUM — misleading |
| dtdayofweek.rst | Example comment says "Get quarters" but code gets day of week | MEDIUM — copy-paste |
| dtdayofyear.rst | Output comment says "Print corresponding years" but prints day of year | MEDIUM — copy-paste |
| h5read.rst | Comment says "4 rows and 3 columns" but code sets r=3; c=2 | MEDIUM |
| strindx.rst | Example calls `strrindx` (reverse) on a `strindx` page | MEDIUM — wrong function |
| timeDiffDT.rst | Return type says "Scalar" but returns NxK matching input; comment says "18 months" but computes minutes | MEDIUM |
| dataopen.rst | Remarks contain `glm(...)` call — copy-paste from another page | MEDIUM |
| inthp2/3/4.rst | All reference `inthp1` in DS description (copy-paste) | LOW |
| lapgeig.rst | seealso references itself (circular) | LOW |
| getorders.rst | Stray "sss" in Purpose | LOW |
| cdfbinomialinv.rst | Missing semicolon in example | LOW |
| moment.rst | Output references undefined `b_est`, variable is `b` | MEDIUM |

## Significant Confusion Points (not bugs, but users would stumble)

### Dangerous silent behaviors
- **stof.rst**: `stof("")` returns 0, not missing — silent data corruption risk for empty strings
- **strtof.rst**: `"1.2 1.9"` silently becomes complex `1.2+1.9i` — wrong results with no error
- **error.rst**: `error(0)` equals missing value code — cannot distinguish error 0 from missing
- **log.rst**: Computes log base 10, not ln — opposite of R, Python, MATLAB, Stata
- **fft.rst**: Scales by 1/N unlike MATLAB — results differ by factor of N

### Parameter/naming confusion
- **reclassifyCuts.rst**: `close_right=1` makes right side OPEN — name is opposite of behavior
- **substute.rst**: Function name misspelled (missing "i")
- **setcollabels.rst**: Parameter descriptions appear swapped between `labels` and `columns`
- **cdftnc.rst**: `nonc` param is square root of noncentrality, not noncentrality itself
- **dftype.rst**: "date" conversion uses POSIX seconds, not DT scalar format — easy to confuse
- **recserar.rst**: Signature uses `rho` but Remarks use `a` for same parameter
- **between.rst**: Param `left` in Format but `x` in description (already fixed)

### Misleading examples
- **olsqr.rst**: Example uses exact system (0 df) — not a real regression use case
- **rndcreatestate.rst**: Sobol `rndCreateState("sobol", 42)` — 42 is dimension not seed (overloaded)
- **intgrat2/3.rst**: First row is UPPER limit — reverse of mathematical convention
- **cdfbinomial.rst**: Output shows probability vs percentage inconsistency
- **plotScatter.rst**: Example 2 axis labels contradict the column order in function call
- **unique.rst**: On matrices, flattens to unique elements (not unique rows like R)

### Missing critical warnings
- **dummy.rst**: Name suggests factor indicators but actually does binning — R/Stata users will be confused
- **delif.rst**: Opposite of R's logical subsetting (`delif` removes TRUE rows, R keeps them)
- **minc.rst**: Returns column minimums (not scalar like R's `min()`) — `c` suffix meaning unexplained
- **sumc.rst**: Returns Kx1 column vector, not row vector — dimension flip trap
- **contains.rst**: Returns scalar (any match), not element-wise like R's `%in%`
- **ols.rst**: Residuals off by default (need `_olsres=1`) — surprising for R/Stata users
- **momentd.rst**: Silently adds constant column via `__con=1` global

### Date format confusion
- **dttostr.rst vs posixtostrc.rst**: Two incompatible format systems (MO/DD/YYYY vs %m/%d/%Y)
- **datestr.rst**: Returns 2-digit year with no ambiguity warning
- **plotTS.rst**: `200504` could be April 2005 or May 4, 2005
- **ethsec.rst**: "Hundredths of a second" — unit no other language uses

## Systematic Issues

- ~15 pages reference "SAS dataset" but load .dta (Stata) files
- GML library functions don't note it's a separate paid package
- DT scalar format vs POSIX dates vs dataframe dates — no cross-reference between the three systems
- `trap` mechanism explained only on scalerr.rst, referenced everywhere

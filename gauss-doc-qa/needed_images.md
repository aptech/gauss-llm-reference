# Needed Images — Guides & Tutorials

Generated 2026-03-15 from persona review of 21 guide/tutorial pages.

## Summary

| Section | Pages | Existing Images | Recommended New Images |
|---------|-------|----------------|----------------------|
| Getting Started | 5 | 3 (in quickstart) | 10 |
| User Guide | 11 | 0 | 18 |
| Coming to GAUSS | 5 | 8 (all in Stata guide) | 24 |
| **Total** | **21** | **11** | **52** |

**Critical gap:** The R, Python, MATLAB, and EViews migration guides have ZERO images. The Stata guide has 8.

## Reusable Assets (create once, use everywhere)

These images can be shared across multiple pages:

| Asset | Used by | Description |
|-------|---------|-------------|
| **Annotated GAUSS 26 IDE screenshot** | All 5 Coming to GAUSS guides + absolute-basics + quickstart | IDE with callouts: editor pane, output window, command bar, variables panel, run button. Per-guide variants just change callout labels (e.g., "like RStudio Source pane" vs "like MATLAB Editor") |
| **Symbol Editor spreadsheet view** | Stata, R, Python, MATLAB, EViews guides | Dataframe displayed in the spreadsheet viewer — equivalent of RStudio View(), MATLAB Variable Editor, EViews Workfile |
| **Sample scatter plot output** | All 5 Coming to GAUSS guides + quickstart | The "Putting It Together" scatter plot rendered in GAUSS — reusable across all guides |
| **OLS output in Output window** | Stata, R, EViews guides | `olsmt` results rendered — maps to `regress`, `lm()`, EViews equation output |

Creating these 4 assets covers ~20 of the 52 recommended images.

## Priority 1: Getting Started (10 images)

### absolute-basics.rst (6 images — currently has ZERO)
| Priority | Type | What to show |
|----------|------|-------------|
| **P1** | Annotated screenshot | GAUSS IDE with callouts: Command Window, Editor, Run button, file browser |
| **P1** | Diagram | Matrix layout: `{ 1 2 3, 4 5 6 }` as labeled 2x3 grid showing spaces=columns, commas=rows |
| **P1** | Diagram | Matrix indexing: color-coded cells showing `A[1,1]`, `A[2,3]`, `A[1,.]`, `A[.,2]` |
| **P2** | Screenshot | Command Window showing `print "Hello, World!";` input and output |
| **P2** | Annotated screenshot | Editor with code + Run button circled + output visible below |
| **P3** | Screenshot | Editor showing housing_analysis.e with output in Command Window |

### quickstart.rst (2 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Screenshot | Customized scatter plot output (with plotControl title/labels) — the only plot example without an image |
| **P3** | Annotated screenshot | Top of GAUSS window showing working directory path |

### running-existing-code.rst (2 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Screenshot | Package Manager dialog (Tools > Package Manager) |
| **P3** | Annotated screenshot | Preferences > Source Path with example paths added |

## Priority 2: User Guide (18 images)

### operators.rst (3 images — highest value)
| Priority | Type | What to show |
|----------|------|-------------|
| **P1** | Diagram | Matrix multiply `A * B` vs element-wise `A .* B` side-by-side mechanics |
| **P1** | Diagram | ExE conformability/broadcasting: scalar→matrix, column→matrix, row→matrix |
| **P2** | Diagram | `x .== y` (element-wise 0/1 matrix) vs `x == y` (scalar collapse) |

### time-and-date.rst (3 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P1** | Diagram | POSIX timeline with epoch, example dates as second values |
| **P1** | Side-by-side | BSD strftime (`%Y-%m-%d`) vs GAUSS legacy (`YYYY-MO-DD`) with function names |
| **P2** | Conversion diagram | Four date formats as boxes with conversion function arrows between them |

### formula-strings.rst (3 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Data flow diagram | CSV → `loadd` with formula → resulting columns |
| **P2** | Expansion diagram | `Income * Rating` → `Income + Rating + Income:Rating` |
| **P3** | Transformation diagram | `factor(cat(load))` step-by-step: strings → integers → dummies |

### procedures.rst (2 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Annotated code | Procedure anatomy: declaration, locals, body, retp with labeled arrows |
| **P3** | Data flow | Function pointer: `&func` → parameter → `local f:proc` → `f(x)` dispatch |

### structures.rst (2 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P1** | Pipeline diagram | Create() → control struct → user overrides → estimation function → output struct |
| **P3** | Diagram | Pass by value (copy) vs pass by pointer (address) with `&` |

### arrays.rst (2 images)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | 3D block diagram | `2|3|4` array with reversed dimension numbering labeled |
| **P3** | Diagram | `aconcat` along dim 1 vs dim 2 vs dim 3 |

### control-flow.rst (1 image)
| Priority | Type | What to show |
|----------|------|-------------|
| **P3** | Diagram | `threadfor` parallel dispatch: iterations → threads → result assembly |

### strings.rst (1 image)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Diagram | `$+` (merge) vs `$~` (horizontal) vs `$|` (vertical) with visual boxes |

### compilation-libraries.rst (1 image)
| Priority | Type | What to show |
|----------|------|-------------|
| **P3** | Flowchart | Autoloader search path: user.lcg → user libs → gauss.lcg → .g files |

## Priority 3: Coming to GAUSS (24 images)

### All 5 guides need:
| Priority | Type | What to show |
|----------|------|-------------|
| **P1** | Annotated screenshot | GAUSS IDE with per-language callout labels (reusable asset) |
| **P2** | Screenshot | Symbol Editor spreadsheet view (reusable asset) |
| **P2** | Screenshot | Sample plot output (reusable asset) |

### intro-gauss-for-stata-users.rst (1 new image + review 8 existing)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Side-by-side | Stata `regress` output next to GAUSS `olsmt` output with field mapping |
| **Review** | — | Check all 8 existing images for GAUSS 26 UI compatibility |

### intro-gauss-for-r-users.rst (2 additional)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Screenshot | Breakpoint in editor margin + error message with clickable line |
| **P2** | Screenshot | OLS output + scatter plot in Output window ("Putting It Together") |

### intro-gauss-for-python-users.rst (1 additional)
| Priority | Type | What to show |
|----------|------|-------------|
| **P3** | Screenshot | `dstatmt` output rendered in Output window (like `df.describe()`) |

### intro-gauss-for-matlab-users.rst (2 additional)
| Priority | Type | What to show |
|----------|------|-------------|
| **P1** | Diagram | `reshape` fill order: MATLAB column-major vs GAUSS row-major |
| **P2** | Screenshot | Plot output with plotControl customization |

### intro-gauss-for-eviews-users.rst (4 additional)
| Priority | Type | What to show |
|----------|------|-------------|
| **P2** | Side-by-side | EViews equation output next to GAUSS `olsmt` output |
| **P2** | Flowchart | EViews VAR workflow (object→estimate→view) vs GAUSS (svarFit→plotIRF) |
| **P3** | Screenshot | IRF plot output with confidence bands |
| **P3** | Screenshot | FEVD plot output |

## Action Plan

### Phase 1: Create 4 reusable assets (covers ~20 image slots)
1. Annotated GAUSS 26 IDE screenshot
2. Symbol Editor spreadsheet view
3. Sample scatter plot output
4. OLS output in Output window

### Phase 2: Create 5 diagrams (highest conceptual value)
1. Matrix layout (spaces=cols, commas=rows)
2. Matrix indexing (color-coded cells)
3. Matrix multiply vs element-wise
4. Control struct pipeline
5. Date format systems comparison

### Phase 3: Create remaining per-page images
Prioritize by page traffic: absolute-basics > operators > time-and-date > Coming to GAUSS guides

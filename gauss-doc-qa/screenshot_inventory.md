# Screenshot & Image Inventory

Generated 2026-03-15 from scan of ~/svn/gxmldoc/docs/

## Summary

| Category | Count |
|----------|-------|
| Images referenced in RST files | 191 |
| Images existing on disk | 228 |
| **Missing (referenced but not found)** | **40** |
| Orphaned (on disk but not referenced) | 77 |

## Missing Images (40)

These are referenced in RST files but do not exist on disk. The Sphinx build will produce warnings for these.

### TSMT Equation SVGs (36 files)

All referenced from TSMT (Time Series MT) module documentation. These appear to be math equations that were intended as rendered SVG images but were never created or were lost.

| Image | Referenced by | What it should show |
|-------|---------------|---------------------|
| Equation704.svg | tsmt/nwmt.rst | Newey-West estimator formula |
| Equation705.svg | tsmt/nwmt.rst | Newey-West estimator formula |
| Equation706.svg | tsmt/nwmt.rst | Newey-West estimator formula |
| Equation707.svg | tsmt/robustse.rst | Robust standard errors formula |
| Equation708.svg | tsmt/tsfill.rst | Time series fill formula |
| Equation709.svg | tsmt/tsfill.rst | Time series fill formula |
| Equation714-739.svg | tsmt/vmppmt.rst (26 images) | VAR model equations |
| Equation740.svg | tsmt/vmztcritmt.rst | Z-test critical value formula |
| Equation741.svg | tsmt/vmsjmt.rst | Johansen test formula |
| Equation742.svg | tsmt/vmsjmt.rst | Johansen test formula |
| Equation743.svg | tsmt/vmrztcritmt.rst | Restricted Z-test formula |

**Recommendation:** Replace with `.. math::` LaTeX directives instead of SVG images. This is more maintainable and renders correctly in all Sphinx output formats.

### Textbook Examples (3 files)

| Image | Referenced by | What it should show |
|-------|---------------|---------------------|
| brooks-erfordersandp-scatter.jpg | textbook-examples/.../estimation-of-capital-asset-pricing-model.rst | Scatter plot of S&P returns |
| brooks-erfordersandp-xy.jpg | textbook-examples/.../estimation-of-capital-asset-pricing-model.rst | XY plot of S&P returns |
| brooks-pca-explained-variance.jpg | textbook-examples/.../principal-components-tbills.rst | PCA explained variance bar chart |

**Recommendation:** Regenerate by running the GAUSS example code and saving the plots.

### UI Screenshots (1 file)

| Image | Referenced by | What it should show |
|-------|---------------|---------------------|
| data-transform-code-generation.jpg | data-management/data-cleaning.rst | GAUSS data transform code generation UI |

**Recommendation:** Take screenshot from GAUSS 26 UI.

## Orphaned Images (77)

These exist in `_static/images/` but are not referenced by any RST file. They may be:
- From old versions of the docs that were rewritten
- Used by the Sphinx theme/template (not directly in RST)
- Leftover from deleted pages

### Likely theme/branding (keep):
- Gauss_Icon_RGB.png
- Gauss_Logo_RGB.png
- aptech-logo.png

### Likely old plot examples (review before deleting):
- boxplot-by.jpg
- g25-percent-frequencies.jpg
- g25-plotfreq-day-by-smoker.jpg
- g_basic_bar_plot.png
- g_graph_contour_only.png
- g_graph_surface_only.png
- g_surface.png, g_surface_2.png
- g_plot_add_2.png, g_plot_add_3.png

### Likely old UI screenshots (review before deleting):
- click_on_canvas.png
- command_error.png
- data-cleaning-missing-gray-cell.jpg
- data-import-import-options-csv.png
- edit_canvas_settings.png
- g_choose_graph_prefs.png
- g_graph_preferences_1.png

**Recommendation:** Do NOT delete orphaned images without checking the Sphinx theme templates, `conf.py`, and any JS/CSS that might reference them. The branding images are almost certainly used by the theme.

## Action Plan

### Priority 1: Fix missing TSMT equations (36 images)
Convert SVG image references to `.. math::` LaTeX directives. This eliminates the dependency on external image files and is the standard Sphinx approach for math. Requires reading the TSMT source to understand what each equation should be.

### Priority 2: Regenerate textbook example plots (3 images)
Run the example GAUSS code and save the output plots.

### Priority 3: Retake UI screenshot (1 image)
Screenshot the data transform code generation feature in GAUSS 26.

### Priority 4: Audit orphaned images (77 images)
Check theme templates before deleting. Most are probably safe to remove but verify first.

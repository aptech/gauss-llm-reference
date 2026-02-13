# GAUSS Graphics Reference

## Basic Plots

### Line Plot (XY)
```gauss
x = seqa(0, 0.1, 100);
y = sin(x);
plotXY(x, y);

// Multiple series
y2 = cos(x);
plotXY(x, y~y2);  // Two columns of y data
```

### Scatter Plot
```gauss
x = rndn(100, 1);
y = x + 0.5*rndn(100, 1);
plotScatter(x, y);
```

### Histogram
```gauss
x = rndn(1000, 1);
plotHist(x, 20);  // 20 bins
```

### Bar Chart
```gauss
labels = "A" $| "B" $| "C" $| "D";
values = { 10, 25, 15, 30 };
plotBar(labels, values);
```

### Box Plot
```gauss
// Single box
x = rndn(100, 1);
plotBox(x);

// Multiple boxes
x = rndn(100, 3);  // 3 columns = 3 boxes
plotBox(x);
```

## Plot Control Structure

All customization is done through a `plotControl` structure:

```gauss
// Initialize with defaults for plot type
struct plotControl pc;
pc = plotGetDefaults("xy");      // or "scatter", "bar", "hist", "box", etc.

// Apply settings using plotSet* functions
plotSetTitle(&pc, "My Title");
plotSetXLabel(&pc, "X Axis");
plotSetYLabel(&pc, "Y Axis");

// Pass structure as first argument to plot function
plotXY(pc, x, y);
```

## Common Settings

### Titles and Labels
```gauss
struct plotControl pc;
pc = plotGetDefaults("xy");

plotSetTitle(&pc, "Main Title");
plotSetXLabel(&pc, "X Variable");
plotSetYLabel(&pc, "Y Variable");

// Font settings
plotSetTitleFont(&pc, "Arial");
plotSetTitleFontSize(&pc, 16);
```

### Legend
```gauss
// Legend text for multiple series
plotSetLegend(&pc, "Series 1" $| "Series 2" $| "Series 3");

// Legend position
plotSetLegend(&pc, "Series 1" $| "Series 2", "top right");
// Positions: "top left", "top right", "bottom left", "bottom right",
//            "inside top left", "inside top right", etc.

// Turn off legend
plotSetLegend(&pc, "", "off");
```

### Axis Ranges
```gauss
plotSetXRange(&pc, 0, 100);      // X from 0 to 100
plotSetYRange(&pc, -10, 10);     // Y from -10 to 10

// Auto range (default)
plotSetXRange(&pc, 0, 0);        // 0, 0 means auto
```

### Grid
```gauss
plotSetGrid(&pc, "on");          // Show grid
plotSetGrid(&pc, "off");         // Hide grid
plotSetGrid(&pc, "minor");       // Show minor gridlines too
```

### Line Styles
```gauss
// Line thickness
plotSetLinePen(&pc, 2);          // Width in pixels

// Line thickness with color
plotSetLinePen(&pc, 2, "blue");

// Line style
plotSetLineStyle(&pc, 1);        // 1=solid, 2=dash, 3=dot, 4=dash-dot

// Line color (single or multiple series)
plotSetLineColor(&pc, "blue");
plotSetLineColor(&pc, "blue" $| "red" $| "green");

// RGB colors
plotSetLineColor(&pc, "#FF5733");
```

### Marker Styles (Scatter)
```gauss
struct plotControl pc;
pc = plotGetDefaults("scatter");

// Marker shape
plotSetLineSymbol(&pc, 1);       // 1=circle, 2=square, 3=triangle, etc.

// Multiple series with different symbols
plotSetLineSymbol(&pc, 1|2|3);

// Marker size
plotSetLineThickness(&pc, 8);    // Size in pixels

// Marker fill
plotSetFill(&pc, 1);             // 1=filled, 0=hollow
```

### Colors
```gauss
// Background color
plotSetBkdColor(&pc, "white");

// Canvas color (plot area)
plotSetFill(&pc, 1, "lightgray");

// Named colors: "red", "blue", "green", "black", "white", "gray",
//               "orange", "purple", "yellow", "cyan", "magenta", etc.
// Hex colors: "#FF5733", "#3498DB"
// RGB: Use hex notation
```

## Advanced Plots

### Time Series Plot
```gauss
// With date x-axis
dates = seqa(timeutc(2020, 1, 1, 0, 0, 0), 86400, 365);  // Daily for 1 year
values = cumsumc(rndn(365, 1));

struct plotControl pc;
pc = plotGetDefaults("xy");
plotSetXTicLabel(&pc, "%Y-%m");  // Format: 2020-01
plotXY(pc, dates, values);
```

### Area Plot
```gauss
x = seqa(1, 1, 20);
y = abs(cumsumc(rndn(20, 1)));
plotArea(x, y);

// Stacked area
y = abs(cumsumc(rndn(20, 3)));
plotArea(x, y);
```

### Surface Plot (3D)
```gauss
x = seqa(-2, 0.1, 41);
y = seqa(-2, 0.1, 41);
z = zeros(41, 41);
for i (1, 41, 1);
    for j (1, 41, 1);
        z[i,j] = sin(sqrt(x[i]^2 + y[j]^2));
    endfor;
endfor;
plotSurface(x, y, z);
```

### Contour Plot
```gauss
plotContour(x, y, z);
```

### Polar Plot
```gauss
theta = seqa(0, 0.1, 63);
r = 2*cos(3*theta);
plotPolar(theta, r);
```

## Multiple Plots

### Subplots
```gauss
// Create 2x2 subplot layout
plotLayout(2, 2, 1);   // 2 rows, 2 cols, plot in position 1
plotXY(x1, y1);

plotLayout(2, 2, 2);   // Position 2
plotScatter(x2, y2);

plotLayout(2, 2, 3);   // Position 3
plotBar(labels, values);

plotLayout(2, 2, 4);   // Position 4
plotHist(data);

// Clear layout
plotClearLayout();
```

### Add to Existing Plot
```gauss
// First plot
plotXY(x, y1);

// Add to same plot
plotAddXY(x, y2);
plotAddScatter(x_points, y_points);

// Add horizontal/vertical lines
plotAddHLine(0);        // Horizontal line at y=0
plotAddVLine(5);        // Vertical line at x=5
```

## Saving Plots

```gauss
// Save to file
plotSave("myplot.png");
plotSave("myplot.pdf");
plotSave("myplot.svg");
plotSave("myplot.jpg");

// With specific dimensions (pixels)
plotSave("myplot.png", 800, 600);
```

## Common Patterns

### Publication-Quality Plot
```gauss
struct plotControl pc;
pc = plotGetDefaults("xy");

// Clean style
plotSetGrid(&pc, "on");
plotSetBkdColor(&pc, "white");

// Labels
plotSetTitle(&pc, "Effect of X on Y");
plotSetXLabel(&pc, "Independent Variable (X)");
plotSetYLabel(&pc, "Dependent Variable (Y)");

// Legend
plotSetLegend(&pc, "Treatment" $| "Control", "top left");

// Line styles for print
plotSetLinePen(&pc, 2, "black" $| "gray");
plotSetLineStyle(&pc, 1|2);     // Solid and dashed

plotXY(pc, x, y1~y2);
plotSave("figure1.pdf", 800, 600);
```

### Regression Plot with Fit Line
```gauss
x = rndn(50, 1);
y = 2 + 3*x + rndn(50, 1);

// Fit regression
b = y / (ones(50,1) ~ x);

// Create fit line
x_line = seqa(minc(x), 0.1, 50);
y_hat = b[1] + b[2]*x_line;

struct plotControl pc;
pc = plotGetDefaults("scatter");
plotSetTitle(&pc, "Regression Results");
plotScatter(pc, x, y);
plotAddXY(x_line, y_hat);
```

### Confidence Interval Shading
```gauss
x = seqa(1, 1, 100);
y = sin(x/10);
upper = y + 0.2;
lower = y - 0.2;

// Plot shaded region
plotSetFill(&pc, 1, "lightblue");
plotArea(x, lower~upper);

// Add mean line on top
plotAddXY(x, y);
```

### Categorical Bar Chart
```gauss
categories = "Q1" $| "Q2" $| "Q3" $| "Q4";
sales_2022 = { 100, 150, 200, 175 };
sales_2023 = { 120, 180, 190, 210 };

struct plotControl pc;
pc = plotGetDefaults("bar");
plotSetTitle(&pc, "Quarterly Sales");
plotSetLegend(&pc, "2022" $| "2023");

// Grouped bars
plotBar(pc, categories, sales_2022 ~ sales_2023);
```

## Tic Label Formatting

```gauss
// Date format on X axis
plotSetXTicLabel(&pc, "%Y-%m-%d");

// Percent format
plotSetYTicLabel(&pc, "%.0f%%");

// Currency
plotSetYTicLabel(&pc, "$%.2f");

// Scientific notation
plotSetYTicLabel(&pc, "%.2e");

// Custom tic positions
plotSetXTicInterval(&pc, 10);    // Tic every 10 units
plotSetXTicCount(&pc, 5);        // Exactly 5 tics
```

## Plot Types Summary

| Function | Description |
|----------|-------------|
| `plotXY` | Line plot |
| `plotScatter` | Scatter plot |
| `plotBar` | Bar chart |
| `plotHist` | Histogram |
| `plotBox` | Box plot |
| `plotArea` | Area chart |
| `plotPolar` | Polar plot |
| `plotSurface` | 3D surface |
| `plotContour` | Contour plot |
| `plotHeatmap` | Heatmap |
| `plotPie` | Pie chart |
| `plotTS` | Time series with date axis |

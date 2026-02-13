# GAUSS Structures Reference

Structures in GAUSS are user-defined types that group related data. They are heavily used for control options and output from statistical procedures.

## Defining Structures

```gauss
// Basic structure definition
struct myStruct {
    scalar x;
    matrix data;
    string name;
    string array names;
};

// Create an instance
struct myStruct s;
s.x = 5;
s.data = rndn(10, 3);
s.name = "example";
s.names = "a" $| "b" $| "c";
```

## Using Structures with Procedures

```gauss
// Procedure that takes a structure
proc (1) = myFunc(x, struct myStruct ctl);
    // Access structure members
    print ctl.name;
    retp(x * ctl.x);
endp;

// Procedure that returns a structure
proc (1) = createStruct(x);
    struct myStruct s;
    s.x = x;
    s.data = zeros(5, 5);
    retp(s);
endp;
```

## Common Statistical Control Structures

### olsmtControl (OLS Regression)

```gauss
struct olsmtControl ctl;
ctl = olsmtControlCreate();  // Initialize with defaults

// Key members:
ctl.con = 1;        // 1 = include constant, 0 = no constant
ctl.miss = 0;       // 0 = no missing, 1 = listwise deletion, 2 = pairwise
ctl.output = 1;     // 1 = print results, 0 = suppress output
ctl.res = 0;        // 1 = compute residuals and Durbin-Watson
ctl.altnam = "";    // Alternative variable names (string array)
ctl.row = 0;        // Rows to read per iteration (0 = auto)

// Example usage
struct olsmtOut out;
out = olsmt("", y, x, ctl);

// Without control structure (uses defaults)
out = olsmt("", y, x);

// With formula string
out = olsmt(df, "y ~ x1 + x2 + x3");
```

### olsmtOut (OLS Output)

```gauss
struct olsmtOut out;
out = olsmt("", y, x);

// Key members:
out.beta;      // Coefficient estimates
out.stderr;    // Standard errors
out.tstat;     // t-statistics
out.pvalue;    // p-values
out.rsq;       // R-squared
out.adjrsq;    // Adjusted R-squared
out.fstat;     // F-statistic
out.fpval;     // F p-value
out.resid;     // Residuals (if ctl.res = 1)
out.dwstat;    // Durbin-Watson (if ctl.res = 1)
out.vnam;      // Variable names
out.m;         // Moment matrix (X'X)
```

### glmControl (Generalized Linear Models)

```gauss
struct glmControl ctl;
ctl = glmControlCreate();  // Initialize with defaults

// Key members:
ctl.varNames = "";       // Variable names
ctl.categoryIdx = 0;     // Indices of categorical columns (0 = none)
ctl.link = "canonical";  // Link function
ctl.constantFlag = 1;    // 1 = include intercept, -1 = no intercept
ctl.printFlag = "Y";     // "Y" or "N" for printing
ctl.maxIters = 25;       // Maximum iterations
ctl.eps = 1e-8;          // Convergence tolerance

// Link function options:
// "canonical" (default for each family)
// "identity", "inverse", "inverse squared"
// "ln", "logit", "probit", "cloglog"

// Example: Logistic regression
struct glmOut out;
out = glm(y, x, "binomial", ctl);

// Without control (uses defaults)
out = glm(y, x, "binomial");

// Family options: "normal", "binomial", "poisson", "gamma", "inverse gaussian"
```

### glmOut (GLM Output)

```gauss
struct glmOut out;
out = glm(y, x, "binomial");

// Model info
out.modelInfo.distribution;   // Distribution family
out.modelInfo.link;           // Link function used
out.modelInfo.yName;          // Dependent variable name
out.modelInfo.xNames;         // Independent variable names
out.modelInfo.n;              // Number of observations
out.modelInfo.df;             // Degrees of freedom

// Model selection criteria
out.modelSelect.deviance;     // Residual deviance
out.modelSelect.pearson;      // Pearson chi-square
out.modelSelect.LL;           // Log-likelihood
out.modelSelect.dispersion;   // Dispersion parameter
out.modelSelect.aic;          // AIC
out.modelSelect.bic;          // BIC

// Coefficients
out.coef.estimates;           // Parameter estimates
out.coef.se;                  // Standard errors
out.coef.testStat;            // Test statistics
out.coef.pvalue;              // p-values

// Other output
out.yhat;                     // Fitted values
out.residuals;                // Residuals
out.covmat;                   // Covariance matrix
out.corrmat;                  // Correlation matrix
out.iteration;                // Number of iterations
```

### dstatmtOut (Descriptive Statistics)

```gauss
struct dstatmtOut dout;
dout = dstatmt(df, "x1 + x2 + x3");

// Key members:
dout.mean;         // Column means
dout.var;          // Variances
dout.std;          // Standard deviations
dout.min;          // Minimums
dout.max;          // Maximums
dout.validcases;   // Number of valid cases
dout.misscases;    // Number of missing cases
dout.median;       // Medians
dout.skewness;     // Skewness
dout.kurtosis;     // Kurtosis
```

### plotControl (Graphics)

```gauss
struct plotControl pc;
pc = plotGetDefaults("xy");  // "xy", "scatter", "bar", "hist", etc.

// Common settings (use plotSet* functions)
plotSetTitle(&pc, "My Plot");
plotSetXLabel(&pc, "X Axis");
plotSetYLabel(&pc, "Y Axis");
plotSetGrid(&pc, "on");
plotSetLegend(&pc, "Series 1" $| "Series 2");
plotSetLineColor(&pc, "blue" $| "red");
plotSetLineStyle(&pc, 1|2);           // 1=solid, 2=dash, etc.
plotSetLineThickness(&pc, 2);

// Use with plot functions
plotXY(pc, x, y);
plotScatter(pc, x, y);
```

## Optimization Control Structures

### sqpsolvemtControl (SQP Optimization)

```gauss
struct sqpsolvemtControl ctl;
ctl = sqpsolvemtControlCreate();

ctl.maxIters = 500;        // Maximum iterations
ctl.printIters = 1;        // Print iteration info
ctl.tol = 1e-5;            // Tolerance
ctl.feasTol = 1e-5;        // Feasibility tolerance
ctl.gradTol = 1e-5;        // Gradient tolerance
ctl.dirTol = 1e-5;         // Direction tolerance
```

### qnewtonmtControl (Quasi-Newton)

```gauss
struct qnewtonmtControl ctl;
ctl = qnewtonmtControlCreate();

ctl.maxIters = 500;
ctl.tol = 1e-5;
ctl.gradTol = 1e-5;
ctl.printIters = 1;
ctl.hessMethod = 1;    // 1=BFGS, 2=DFP, 3=numeric
```

## Creating Control Structure Defaults

Most GAUSS procedures have a `*ControlCreate()` function:

```gauss
// Pattern: procedureControlCreate()
struct olsmtControl ctl;
ctl = olsmtControlCreate();

struct glmControl gctl;
gctl = glmControlCreate();

struct plotControl pc;
pc = plotGetDefaults("scatter");
```

## Structure Arrays

```gauss
// Create array of structures
struct myStruct sarr;
sarr = reshape(sarr, 5, 1);  // 5x1 array

// Access elements
sarr[1].x = 10;
sarr[2].x = 20;

// Loop through
for i (1, rows(sarr), 1);
    print sarr[i].x;
endfor;
```

## Nested Structures

```gauss
struct innerStruct {
    scalar value;
    matrix data;
};

struct outerStruct {
    string name;
    struct innerStruct inner;
};

// Usage
struct outerStruct os;
os.name = "test";
os.inner.value = 42;
os.inner.data = eye(3);
```

## Common Patterns

### Regression with Custom Options
```gauss
// OLS with options
struct olsmtControl ctl;
ctl = olsmtControlCreate();
ctl.con = 1;         // Include constant
ctl.res = 1;         // Compute residuals
ctl.output = 0;      // Suppress printing

struct olsmtOut out;
out = olsmt("", y, x, ctl);

print "Coefficients:";
print out.beta;
print "R-squared:" out.rsq;
```

### GLM Model Comparison
```gauss
// Compare logit and probit
struct glmControl ctl;
ctl = glmControlCreate();
ctl.printFlag = "N";

struct glmOut logit_out, probit_out;

ctl.link = "logit";
logit_out = glm(y, x, "binomial", ctl);

ctl.link = "probit";
probit_out = glm(y, x, "binomial", ctl);

print "Logit AIC:" logit_out.modelSelect.aic;
print "Probit AIC:" probit_out.modelSelect.aic;
```

### Saving and Loading Structures
```gauss
// Save structure to file
struct myStruct s;
s.x = 5;
s.data = rndn(100, 10);

// Use saveStruct/loadStruct
saveStruct(s, "mystruct.gcf");

// Load it back
struct myStruct s2;
s2 = loadStruct("mystruct.gcf");
```

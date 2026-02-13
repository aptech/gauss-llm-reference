# GAUSS FANPAC (Factor Analysis) Reference

FANPAC is GAUSS's Factor Analysis module for exploratory and confirmatory factor analysis.

## Exploratory Factor Analysis (EFA)

### Principal Components Analysis
```gauss
// Basic PCA
struct pcaOut out;
out = pcaFit(x);

// With control structure
struct pcaControl ctl;
ctl = pcaControlCreate();
ctl.nFactors = 3;           // Number of factors to extract
ctl.rotate = "varimax";     // Rotation method

out = pcaFit(x, ctl);

// Results
print out.loadings;         // Factor loadings
print out.eigenvalues;      // Eigenvalues
print out.communalities;    // Communalities
print out.scores;           // Factor scores
print out.variance;         // Variance explained
```

### Factor Analysis (Maximum Likelihood)
```gauss
struct faOut out;
out = faFit(x, nfactors);

// With rotation
struct faControl ctl;
ctl = faControlCreate();
ctl.rotate = "varimax";     // "varimax", "quartimax", "promax", "oblimin"
ctl.output = 1;             // Print results

out = faFit(x, nfactors, ctl);
```

### Rotation Methods
```gauss
// Orthogonal rotations (uncorrelated factors)
ctl.rotate = "varimax";     // Most common
ctl.rotate = "quartimax";
ctl.rotate = "equamax";

// Oblique rotations (correlated factors)
ctl.rotate = "promax";
ctl.rotate = "oblimin";

// No rotation
ctl.rotate = "none";
```

## Determining Number of Factors

### Scree Plot
```gauss
out = pcaFit(x);

// Plot eigenvalues
plotXY(seqa(1, 1, rows(out.eigenvalues)), out.eigenvalues);
plotAddHLine(1);            // Kaiser criterion line
```

### Parallel Analysis
```gauss
struct paOut pa;
pa = parallelAnalysis(x, nreps);

print pa.eigenvalues;       // Sample eigenvalues
print pa.random_eigs;       // Random data eigenvalues (95th percentile)
print pa.n_factors;         // Suggested number of factors
```

### Kaiser Criterion
```gauss
out = pcaFit(x);
n_factors = sumc(out.eigenvalues .> 1);
```

## Confirmatory Factor Analysis (CFA)

### Model Specification
```gauss
// Define factor structure
// Lambda matrix: rows = observed variables, cols = latent factors
lambda = { 1 0,             // X1 loads on F1 only
           . 0,             // X2 loads on F1 (freely estimated)
           . 0,             // X3 loads on F1
           0 1,             // X4 loads on F2 only
           0 .,             // X5 loads on F2
           0 . };           // X6 loads on F2

struct cfaOut out;
out = cfaFit(x, lambda);
```

### CFA Results
```gauss
print out.loadings;         // Estimated factor loadings
print out.factor_cov;       // Factor covariance matrix
print out.residual_var;     // Residual (unique) variances

// Fit indices
print out.chi2;             // Chi-square test
print out.pval;             // Chi-square p-value
print out.cfi;              // Comparative Fit Index
print out.tli;              // Tucker-Lewis Index
print out.rmsea;            // RMSEA
print out.srmr;             // SRMR
```

### Fit Index Guidelines
```gauss
// Good fit typically requires:
// CFI > 0.95 (or > 0.90 acceptable)
// TLI > 0.95 (or > 0.90 acceptable)
// RMSEA < 0.06 (or < 0.08 acceptable)
// SRMR < 0.08
```

## Reliability Analysis

### Cronbach's Alpha
```gauss
alpha = cronbachAlpha(x);
print alpha;

// Item-total statistics
struct alphaOut out;
out = cronbachAlphaFull(x);
print out.alpha;
print out.item_total;       // Item-total correlations
print out.alpha_if_deleted; // Alpha if item deleted
```

### Composite Reliability
```gauss
// From CFA output
loadings = out.loadings;
resid_var = out.residual_var;

sum_loadings = sumc(loadings);
sum_resid = sumc(resid_var);
CR = sum_loadings^2 / (sum_loadings^2 + sum_resid);
```

### Average Variance Extracted (AVE)
```gauss
AVE = sumc(loadings.^2) / rows(loadings);
```

## Factor Scores

### Regression Method (Thompson)
```gauss
out = faFit(x, nfactors);
scores = out.scores;        // Default: regression method
```

### Bartlett Method
```gauss
struct faControl ctl;
ctl = faControlCreate();
ctl.score_method = "bartlett";

out = faFit(x, nfactors, ctl);
scores = out.scores;
```

## Common Patterns

### Complete EFA Analysis
```gauss
// 1. Check KMO and Bartlett's test
kmo = kmo(x);
print "KMO:" kmo;

bt = bartlettTest(x);
print "Bartlett's test p-value:" bt.pval;

// 2. Determine number of factors
out = pcaFit(x);
print "Eigenvalues:" out.eigenvalues;
plotXY(seqa(1, 1, rows(out.eigenvalues)), out.eigenvalues);

// 3. Extract and rotate factors
struct faControl ctl;
ctl = faControlCreate();
ctl.rotate = "varimax";
ctl.output = 1;

out = faFit(x, nfactors, ctl);

// 4. Examine loadings
print out.loadings;

// 5. Compute scores
scores = out.scores;
```

### Scale Development Workflow
```gauss
// 1. EFA on development sample
out = faFit(x_dev, nfactors);

// 2. Examine loadings, remove poor items
// Keep items with loadings > 0.40 on intended factor
// Remove cross-loading items (loadings > 0.32 on multiple factors)

// 3. Compute reliability
alpha = cronbachAlpha(x_dev[., good_items]);

// 4. CFA on validation sample
out = cfaFit(x_val, lambda);

// 5. Check fit indices
print "CFI:" out.cfi;
print "RMSEA:" out.rmsea;
```

# GAUSS Cointegration Reference

Cointegration analysis is used when dealing with non-stationary time series that share a long-run equilibrium relationship.

## Concept Review

- **Non-stationary series**: Series with unit roots (I(1))
- **Cointegration**: Two or more I(1) series are cointegrated if a linear combination is I(0) (stationary)
- **Error correction**: Short-run deviations from long-run equilibrium are corrected over time

## Unit Root Testing

### ADF Test
```gauss
struct adfOut out;
out = adf(y, maxlags, trend);

// trend options:
// 0 = no constant, no trend
// 1 = constant only (most common)
// 2 = constant and trend

print "ADF statistic:" out.tstat;
print "P-value:" out.pval;

// If p-value > 0.05, fail to reject null of unit root (non-stationary)
```

### Testing for Integration Order
```gauss
// Test in levels
out_levels = adf(y, lags, 1);
print "Levels p-value:" out_levels.pval;

// Test in first differences
out_diff = adf(diff(y, 1), lags, 1);
print "First diff p-value:" out_diff.pval;

// If levels p > 0.05 but diff p < 0.05, series is I(1)
```

## Engle-Granger Two-Step Method

### Step 1: Estimate Long-Run Relationship
```gauss
// Regress y1 on y2 (and possibly constant)
n = rows(y1);
X = ones(n, 1) ~ y2;
b = y1 / X;

// Long-run equilibrium: y1 = b[1] + b[2]*y2
// Get residuals (equilibrium errors)
resid = y1 - X * b;
```

### Step 2: Test Residuals for Stationarity
```gauss
// Use ADF on residuals (no constant since residuals have mean 0)
out = adf(resid, lags, 0);

// Use Engle-Granger critical values (more stringent than standard ADF)
print "EG test statistic:" out.tstat;

// Critical values (approximate, 2 variables):
// 1%: -3.96, 5%: -3.37, 10%: -3.07
```

### Step 3: Error Correction Model
```gauss
// If cointegrated, estimate ECM
dy1 = diff(y1, 1);
dy2 = diff(y2, 1);
ecm = lagn(resid, 1);        // Lagged equilibrium error

// ECM regression: dy1 = a + b*dy2 + c*ecm + error
// c is error correction coefficient (should be negative and significant)
X_ecm = ones(rows(dy1)-1, 1) ~ dy2[2:rows(dy2)] ~ ecm[2:rows(ecm)];
y_ecm = dy1[2:rows(dy1)];

b_ecm = y_ecm / X_ecm;
print "Error correction coefficient:" b_ecm[3];
```

## Johansen Cointegration Test

### Test for Cointegration Rank
```gauss
struct johansenOut out;
out = johansen(y, lags, det);

// y: NxK matrix of variables
// lags: number of lags in VAR
// det: deterministic specification
//      1 = no intercept or trend
//      2 = restricted constant
//      3 = unrestricted constant
//      4 = restricted trend
//      5 = unrestricted constant and restricted trend

print "Trace statistics:";
print out.trace;

print "Max eigenvalue statistics:";
print out.eigen;

print "Critical values (trace):";
print out.trace_crit;

print "Estimated rank:" out.rank;
```

### Interpreting Results
```gauss
// Trace test: Tests H0: rank <= r vs H1: rank > r
// Start from r=0, if rejected move to r=1, etc.
// Stop when fail to reject

// Max eigenvalue: Tests H0: rank = r vs H1: rank = r+1
// Similar sequential testing procedure

// Example interpretation for 3 variables:
// If trace[1] > crit[1] AND trace[2] < crit[2]:
//   Cointegration rank = 1 (one cointegrating relationship)
```

## Vector Error Correction Model (VECM)

### Estimation
```gauss
struct vecmOut out;
out = vecmFit(y, lags, rank);

// y: NxK matrix of variables
// lags: number of lagged differences
// rank: cointegration rank (from Johansen test)

print "Alpha (adjustment speeds):";
print out.alpha;

print "Beta (cointegrating vectors):";
print out.beta;

print "Gamma (short-run dynamics):";
print out.gamma;
```

### Normalized Cointegrating Vector
```gauss
// Normalize so first variable has coefficient 1
beta_norm = out.beta ./ out.beta[1, .];
print "Normalized cointegrating vectors:";
print beta_norm;
```

### VECM Structure
```
The VECM relates changes in variables to:
1. Lagged changes (short-run dynamics): Gamma matrices
2. Error correction (long-run adjustment): Alpha * Beta' * y(t-1)

dy(t) = Alpha * Beta' * y(t-1) + Gamma_1 * dy(t-1) + ... + error
```

## Testing Restrictions

### Testing Beta Restrictions
```gauss
// Test if specific cointegrating relationship holds
// H0: beta = beta_restricted

struct johansenRestrictOut out;
out = johansenRestrict(y, lags, det, H);

// H is the restriction matrix
print "LR statistic:" out.lr;
print "P-value:" out.pval;
```

### Testing Alpha Restrictions (Weak Exogeneity)
```gauss
// Test if a variable does not adjust to disequilibrium
// H0: alpha[i] = 0 (variable i is weakly exogenous)

struct vecmControl ctl;
ctl = vecmControlCreate();
ctl.alpha_restrict = { 0, ., . };  // Restrict alpha[1] = 0

out = vecmFit(y, lags, rank, ctl);
```

## Forecasting with VECM

```gauss
// Generate forecasts
fc = vecmPredict(out, h);    // h periods ahead

print "Point forecasts:";
print fc.forecast;

print "Standard errors:";
print fc.se;
```

## Common Patterns

### Complete Cointegration Analysis
```gauss
// 1. Test for unit roots in each series
for i (1, cols(y), 1);
    out = adf(y[., i], 4, 1);
    print sprintf("Variable %d: ADF = %.3f, p = %.3f",
                  i, out.tstat, out.pval);
endfor;

// 2. Test for cointegration (Johansen)
jout = johansen(y, 2, 3);
print "Trace statistics:" jout.trace;
print "Critical values:" jout.trace_crit;
r = jout.rank;
print "Cointegration rank:" r;

// 3. Estimate VECM if cointegrated
if r > 0;
    vout = vecmFit(y, 2, r);
    print "Cointegrating vectors:";
    print vout.beta;
    print "Adjustment speeds:";
    print vout.alpha;
endif;
```

### Pairs Trading Application
```gauss
// Test if two assets are cointegrated
y = price1 ~ price2;

// Johansen test
out = johansen(y, 1, 3);
if out.rank > 0;
    print "Assets are cointegrated";

    // Get hedge ratio from cointegrating vector
    beta = out.beta[., 1];
    hedge_ratio = -beta[2] / beta[1];
    print "Hedge ratio:" hedge_ratio;

    // Spread (mean-reverting)
    spread = price1 - hedge_ratio * price2;
endif;
```

### Error Correction Interpretation
```gauss
// Alpha values tell adjustment speed
// Negative alpha: variable adjusts toward equilibrium
// Larger |alpha|: faster adjustment

// Example interpretation:
// alpha = { -0.3, 0.1 }
// Variable 1 adjusts 30% of disequilibrium per period
// Variable 2 adjusts 10% (in opposite direction)
// Variable 1 does most of the adjusting
```

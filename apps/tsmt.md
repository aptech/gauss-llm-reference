# GAUSS Time Series MT (TSMT) Reference

TSMT is a comprehensive time series analysis module for GAUSS. This reference covers the most commonly used functions.

## ARIMA Models

### Estimation
```gauss
// Basic ARIMA(p,d,q)
struct arimamtOut out;
out = arimaFit(y, p, d, q);

// With control structure
struct arimamtControl ctl;
ctl = arimamtControlCreate();
ctl.const = 1;              // Include constant
ctl.output = 1;             // Print results

out = arimaFit(y, p, d, q, ctl);

// Access results
print out.aic;              // AIC
print out.bic;              // BIC
print out.coeffs;           // Coefficients
print out.stderr;           // Standard errors
```

### ARIMA with Exogenous Variables (ARIMAX)
```gauss
// ARIMAX model
out = arimaFit(y, p, d, q, ctl, x);

// x is NxK matrix of exogenous regressors
```

### Seasonal ARIMA
```gauss
// SARIMA(p,d,q)(P,D,Q)s
struct arimamtControl ctl;
ctl = arimamtControlCreate();
ctl.s = 12;                 // Seasonal period
ctl.P = 1;                  // Seasonal AR order
ctl.D = 1;                  // Seasonal differencing
ctl.Q = 1;                  // Seasonal MA order

out = arimaFit(y, p, d, q, ctl);
```

### Forecasting
```gauss
// Generate forecasts
struct arimamtForecast fc;
fc = arimaPredict(out, h);   // h periods ahead

print fc.forecast;           // Point forecasts
print fc.se;                 // Standard errors
print fc.lower;              // Lower confidence bound
print fc.upper;              // Upper confidence bound
```

### Model Selection
```gauss
// Auto ARIMA (searches for best model)
struct arimamtOut out;
out = arimaFitAuto(y, max_p, max_q);

// With differencing constraint
out = arimaFitAuto(y, max_p, max_q, d);
```

## GARCH Models

### Basic GARCH(p,q)
```gauss
struct garchOut out;
out = garchFit(y, p, q);

// Common: GARCH(1,1)
out = garchFit(y, 1, 1);

// Access results
print out.params;           // Parameters
print out.sigma;            // Conditional volatility series
print out.ll;               // Log-likelihood
```

### GARCH Variants
```gauss
struct garchControl ctl;
ctl = garchControlCreate();

// EGARCH (exponential GARCH)
ctl.model = "egarch";
out = garchFit(y, p, q, ctl);

// GJR-GARCH (asymmetric)
ctl.model = "gjr";
out = garchFit(y, p, q, ctl);

// IGARCH (integrated)
ctl.model = "igarch";
out = garchFit(y, p, q, ctl);
```

### GARCH with Mean Equation
```gauss
// ARMA-GARCH
struct garchControl ctl;
ctl = garchControlCreate();
ctl.ar = 1;                 // AR order for mean
ctl.ma = 1;                 // MA order for mean

out = garchFit(y, 1, 1, ctl);
```

### GARCH Forecasting
```gauss
fc = garchPredict(out, h);
print fc.variance_forecast;  // Volatility forecasts
```

## Unit Root Tests

### ADF Test (Augmented Dickey-Fuller)
```gauss
struct adfOut out;
out = adf(y, lags, trend);

// lags: number of lagged differences
// trend: 0=none, 1=constant, 2=constant+trend

print out.tstat;            // Test statistic
print out.pval;             // P-value
print out.lags;             // Lags used
```

### Phillips-Perron Test
```gauss
struct ppOut out;
out = pp(y, lags, trend);

print out.tstat;
print out.pval;
```

### KPSS Test
```gauss
// Null: stationarity (opposite of ADF)
struct kpssOut out;
out = kpss(y, lags, trend);

print out.tstat;
print out.crit;             // Critical values
```

### Zivot-Andrews Test (Structural Break)
```gauss
struct zaOut out;
out = za(y, model);

// model: "intercept", "trend", or "both"
print out.tstat;
print out.breakpoint;       // Estimated break date
```

## VAR Models

### Estimation
```gauss
// Vector Autoregression
struct varOut out;
out = varFit(y, lags);

// y is NxK matrix (K variables)
print out.coeffs;           // Coefficient matrices
print out.sigma;            // Residual covariance
print out.aic;
print out.bic;
```

### VAR Forecasting
```gauss
fc = varPredict(out, h);
print fc.forecast;
print fc.se;
```

### Impulse Response Functions
```gauss
irf = varIRF(out, periods);

// Orthogonalized IRF
irf = varIRF(out, periods, "orth");
```

### Granger Causality
```gauss
struct gcOut out;
out = grangerCausality(y, lags);

print out.fstat;
print out.pval;
```

## Cointegration

### Johansen Test
```gauss
struct johansenOut out;
out = johansen(y, lags, det);

// det: deterministic components
// 0=none, 1=constant, 2=restricted trend, etc.

print out.trace;            // Trace statistics
print out.eigen;            // Max eigenvalue statistics
print out.rank;             // Estimated cointegration rank
```

### VECM (Vector Error Correction Model)
```gauss
struct vecmOut out;
out = vecmFit(y, lags, rank);

print out.alpha;            // Adjustment coefficients
print out.beta;             // Cointegrating vectors
```

### Engle-Granger Two-Step
```gauss
// Step 1: Estimate long-run relationship
b = y1 / (ones(rows(y1), 1) ~ y2);
resid = y1 - (ones(rows(y1), 1) ~ y2) * b;

// Step 2: Test residuals for stationarity
out = adf(resid, lags, 0);
```

## State Space Models

### Local Level Model
```gauss
struct ssOut out;
out = ssFit(y, "local_level");

print out.signal;           // Smoothed state
print out.params;           // Variances
```

### Kalman Filter
```gauss
// Custom state space model
struct kalmanOut out;
out = kalmanFilter(y, Z, T, H, Q, a0, P0);

// Z: observation matrix
// T: transition matrix
// H: observation variance
// Q: state variance
// a0, P0: initial state mean and covariance
```

## Spectral Analysis

### Periodogram
```gauss
pg = periodogram(y);
plotXY(pg[., 1], pg[., 2]);  // Frequency vs power
```

### Spectral Density
```gauss
sp = spectral(y, window, bandwidth);
```

## Common Patterns

### Model Comparison
```gauss
// Compare multiple ARIMA models
models = { 1 0 1,           // ARIMA(1,0,1)
           2 0 1,           // ARIMA(2,0,1)
           1 0 2,           // ARIMA(1,0,2)
           2 0 2 };         // ARIMA(2,0,2)

aic = zeros(rows(models), 1);
bic = zeros(rows(models), 1);

for i (1, rows(models), 1);
    p = models[i, 1];
    d = models[i, 2];
    q = models[i, 3];

    out = arimaFit(y, p, d, q);
    aic[i] = out.aic;
    bic[i] = out.bic;
endfor;

best_aic = minc(aic);
best_idx = indexcat(aic, best_aic);
```

### Diagnostic Tests
```gauss
// Ljung-Box test for residual autocorrelation
resid = out.residuals;
struct lbOut lb;
lb = ljungBox(resid, lags);
print "Ljung-Box p-value:" lb.pval;

// Heteroskedasticity test (ARCH-LM)
struct archOut arch;
arch = archTest(resid, lags);
print "ARCH test p-value:" arch.pval;
```

### Rolling Window Estimation
```gauss
// Rolling GARCH estimation
window = 500;
n = rows(y);
vol_forecast = zeros(n - window, 1);

for i (window, n-1, 1);
    y_window = y[i-window+1:i];
    out = garchFit(y_window, 1, 1);
    fc = garchPredict(out, 1);
    vol_forecast[i-window+1] = sqrt(fc.variance_forecast);
endfor;
```

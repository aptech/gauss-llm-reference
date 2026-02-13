# GAUSS GARCH Modeling Reference

GARCH (Generalized Autoregressive Conditional Heteroskedasticity) models are used for modeling time-varying volatility in financial time series.

## Basic Concepts

- **Volatility clustering**: Large changes tend to follow large changes
- **Conditional variance**: Variance that depends on past information
- **Returns**: GARCH is typically applied to returns, not prices

## GARCH(p,q) Model

### Model Specification
```
Return equation:    r(t) = mu + epsilon(t)
Variance equation:  sigma²(t) = omega + alpha*epsilon²(t-1) + beta*sigma²(t-1)

Where:
- omega > 0 (constant term)
- alpha >= 0 (ARCH effect - impact of past shocks)
- beta >= 0 (GARCH effect - persistence)
- alpha + beta < 1 (stationarity condition)
```

### Estimation
```gauss
// Basic GARCH(1,1)
struct garchOut out;
out = garchFit(returns, 1, 1);

// With control structure
struct garchControl ctl;
ctl = garchControlCreate();
ctl.output = 1;              // Print results
ctl.dist = "normal";         // Error distribution

out = garchFit(returns, 1, 1, ctl);

// Access results
print "Parameters:";
print out.params;            // [omega, alpha, beta]
print "Log-likelihood:" out.ll;
print "AIC:" out.aic;
print "BIC:" out.bic;

// Conditional variance series
sigma2 = out.sigma;
volatility = sqrt(sigma2);
```

### GARCH with Mean Equation
```gauss
struct garchControl ctl;
ctl = garchControlCreate();
ctl.ar = 1;                  // AR(1) in mean
ctl.ma = 0;                  // No MA

out = garchFit(returns, 1, 1, ctl);
// Now returns = c + phi*returns(-1) + epsilon
// with GARCH(1,1) errors
```

## GARCH Variants

### EGARCH (Exponential GARCH)
```gauss
// Captures asymmetry: negative shocks may increase volatility more
struct garchControl ctl;
ctl = garchControlCreate();
ctl.model = "egarch";

out = garchFit(returns, 1, 1, ctl);

// EGARCH specification:
// ln(sigma²(t)) = omega + alpha*|z(t-1)| + gamma*z(t-1) + beta*ln(sigma²(t-1))
// gamma captures asymmetry (leverage effect)
```

### GJR-GARCH (Threshold GARCH)
```gauss
// Another asymmetric model
struct garchControl ctl;
ctl = garchControlCreate();
ctl.model = "gjr";

out = garchFit(returns, 1, 1, ctl);

// GJR specification:
// sigma²(t) = omega + (alpha + gamma*I(t-1))*epsilon²(t-1) + beta*sigma²(t-1)
// I(t-1) = 1 if epsilon(t-1) < 0, else 0
```

### IGARCH (Integrated GARCH)
```gauss
// Imposes alpha + beta = 1 (unit root in variance)
struct garchControl ctl;
ctl = garchControlCreate();
ctl.model = "igarch";

out = garchFit(returns, 1, 1, ctl);
```

### GARCH-M (GARCH in Mean)
```gauss
// Volatility affects expected returns
struct garchControl ctl;
ctl = garchControlCreate();
ctl.inmean = 1;              // Include conditional std dev in mean

out = garchFit(returns, 1, 1, ctl);
// mean = c + lambda*sigma(t) + epsilon
```

## Error Distributions

### Normal Distribution
```gauss
struct garchControl ctl;
ctl = garchControlCreate();
ctl.dist = "normal";

out = garchFit(returns, 1, 1, ctl);
```

### Student-t Distribution
```gauss
// Better for fat tails
struct garchControl ctl;
ctl = garchControlCreate();
ctl.dist = "t";

out = garchFit(returns, 1, 1, ctl);
// df (degrees of freedom) is estimated
```

### GED (Generalized Error Distribution)
```gauss
struct garchControl ctl;
ctl = garchControlCreate();
ctl.dist = "ged";

out = garchFit(returns, 1, 1, ctl);
```

### Skewed Distributions
```gauss
struct garchControl ctl;
ctl = garchControlCreate();
ctl.dist = "skewt";          // Skewed Student-t

out = garchFit(returns, 1, 1, ctl);
```

## Forecasting Volatility

### Multi-Step Forecasts
```gauss
h = 20;                      // Forecast horizon
fc = garchPredict(out, h);

print "Variance forecasts:";
print fc.variance_forecast;

print "Volatility forecasts:";
print sqrt(fc.variance_forecast);
```

### Unconditional Variance
```gauss
// Long-run (unconditional) variance
omega = out.params[1];
alpha = out.params[2];
beta = out.params[3];

unconditional_var = omega / (1 - alpha - beta);
unconditional_vol = sqrt(unconditional_var);
print "Unconditional volatility:" unconditional_vol;
```

### Half-Life of Volatility Shocks
```gauss
// How long for a volatility shock to decay by half
persistence = alpha + beta;
half_life = ln(0.5) / ln(persistence);
print "Half-life (periods):" half_life;
```

## Model Diagnostics

### Standardized Residuals
```gauss
epsilon = out.residuals;
sigma = out.sigma;
z = epsilon ./ sqrt(sigma);  // Standardized residuals

// Should be approximately i.i.d. N(0,1)
print "Mean of z:" meanc(z);
print "Std of z:" stdc(z);
print "Skewness:" skewness(z);
print "Kurtosis:" kurtosis(z);
```

### Ljung-Box Test on Squared Residuals
```gauss
// Test for remaining ARCH effects
z2 = z.^2;
lb = ljungBox(z2, 10);
print "Ljung-Box on z²:" lb.stat "p-value:" lb.pval;
// p > 0.05 suggests no remaining ARCH effects
```

### ARCH-LM Test
```gauss
// Lagrange multiplier test for ARCH
arch = archTest(epsilon, 5);
print "ARCH-LM statistic:" arch.stat;
print "P-value:" arch.pval;
```

### News Impact Curve
```gauss
// Shows how shocks affect future volatility
epsilon_grid = seqa(-3, 0.1, 61);  // From -3 to 3

// For GARCH(1,1)
omega = out.params[1];
alpha = out.params[2];
sigma2_prev = unconditional_var;   // Start at unconditional

nic = omega + alpha * epsilon_grid.^2 + beta * sigma2_prev;
plotXY(epsilon_grid, sqrt(nic));
plotSetTitle(&pc, "News Impact Curve");
```

## Common Patterns

### Complete GARCH Analysis
```gauss
// 1. Prepare returns data
prices = loadd("prices.csv", "Close");
returns = 100 * (ln(prices) - lagn(ln(prices), 1));
returns = packr(returns);

// 2. Preliminary statistics
print "Mean return:" meanc(returns);
print "Std dev:" stdc(returns);
print "Skewness:" skewness(returns);
print "Kurtosis:" kurtosis(returns);

// 3. Test for ARCH effects
arch = archTest(returns - meanc(returns), 5);
print "ARCH test p-value:" arch.pval;

// 4. Estimate GARCH(1,1)
struct garchControl ctl;
ctl = garchControlCreate();
ctl.dist = "t";              // Use t-distribution

out = garchFit(returns, 1, 1, ctl);

// 5. Check standardized residuals
z = out.residuals ./ sqrt(out.sigma);
lb = ljungBox(z.^2, 10);
print "Diagnostic test p-value:" lb.pval;

// 6. Forecast
fc = garchPredict(out, 20);
print "20-day volatility forecast:" sqrt(fc.variance_forecast[20]);
```

### Comparing GARCH Models
```gauss
// Estimate different models
struct garchControl ctl;
ctl = garchControlCreate();
ctl.output = 0;

// GARCH(1,1)
out_garch = garchFit(returns, 1, 1, ctl);

// EGARCH(1,1)
ctl.model = "egarch";
out_egarch = garchFit(returns, 1, 1, ctl);

// GJR-GARCH(1,1)
ctl.model = "gjr";
out_gjr = garchFit(returns, 1, 1, ctl);

// Compare by AIC
print "GARCH AIC:" out_garch.aic;
print "EGARCH AIC:" out_egarch.aic;
print "GJR-GARCH AIC:" out_gjr.aic;
```

### Value at Risk (VaR)
```gauss
// Calculate VaR from GARCH forecast
confidence = 0.99;
z_crit = cdfNi(1 - confidence);  // Normal quantile

// 1-day VaR
sigma_1 = sqrt(out.sigma[rows(out.sigma)]);  // Last conditional vol
VaR_1day = -z_crit * sigma_1;

// Multi-day VaR (square-root of time rule for normal)
VaR_10day = VaR_1day * sqrt(10);

print "1-day 99% VaR:" VaR_1day "%";
print "10-day 99% VaR:" VaR_10day "%";
```

### Rolling GARCH Estimation
```gauss
window = 252;                // 1 year of daily data
n = rows(returns);
rolling_vol = zeros(n - window, 1);

struct garchControl ctl;
ctl = garchControlCreate();
ctl.output = 0;

for i (window, n, 1);
    r_window = returns[i-window+1:i];
    out = garchFit(r_window, 1, 1, ctl);
    rolling_vol[i-window+1] = sqrt(out.sigma[rows(out.sigma)]);
endfor;
```

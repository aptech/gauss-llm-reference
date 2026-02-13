# GAUSS Time Series Reference

## Date/Time Representation

GAUSS uses POSIX timestamps (seconds since 1970-01-01 00:00:00 UTC) for dates.

### Creating Dates
```gauss
// From components (year, month, day, hour, min, sec)
dt = timeutc(2024, 6, 15, 0, 0, 0);   // June 15, 2024 midnight UTC

// Current time
now = todaydt();

// From string
dt = strcToPosix("2024-06-15", "%Y-%m-%d");
dt = strcToPosix("06/15/2024", "%m/%d/%Y");
dt = strcToPosix("2024-06-15 14:30:00", "%Y-%m-%d %H:%M:%S");
```

### Formatting Dates
```gauss
// To string
s = posixToStrc(dt, "%Y-%m-%d");           // "2024-06-15"
s = posixToStrc(dt, "%B %d, %Y");          // "June 15, 2024"
s = posixToStrc(dt, "%Y-%m-%d %H:%M:%S");  // "2024-06-15 00:00:00"

// Common format codes:
// %Y = 4-digit year
// %y = 2-digit year
// %m = month (01-12)
// %B = full month name
// %b = abbreviated month
// %d = day (01-31)
// %H = hour (00-23)
// %M = minute (00-59)
// %S = second (00-59)
// %j = day of year (001-366)
// %w = weekday (0=Sunday)
```

### Extracting Components
```gauss
yr = year(dt);                 // Year (e.g., 2024)
mo = month(dt);                // Month (1-12)
dy = dayofmonth(dt);           // Day of month (1-31)
dow = dayofweek(dt);           // Day of week (1=Sunday, 7=Saturday)
doy = dayofyear(dt);           // Day of year (1-366)
hr = hour(dt);                 // Hour (0-23)
mn = minute(dt);               // Minute (0-59)
sc = second(dt);               // Second (0-59)
```

### Date Arithmetic
```gauss
// POSIX is in seconds
one_day = 86400;               // Seconds in a day
one_week = 7 * 86400;
one_hour = 3600;

// Add/subtract time
tomorrow = today + one_day;
next_week = today + one_week;
two_hours_ago = now - 2*one_hour;

// Difference between dates
days_diff = (date2 - date1) / one_day;
hours_diff = (date2 - date1) / one_hour;
```

## Time Series Data Structures

### Creating Time Series Data
```gauss
// Load with date column
df = loadd("prices.csv", "date(Date) + Price + Volume");

// Create date sequence
n = 252;  // Trading days
start = timeutc(2024, 1, 1, 0, 0, 0);
dates = seqa(start, 86400, n);  // Daily dates

// Combine dates with values
prices = cumsumc(rndn(n, 1)) + 100;
df = asdf(dates ~ prices, "Date" $| "Price");
```

### Sorting by Date
```gauss
df = sortc(df, "Date");        // Sort ascending by date
```

## Lags and Differences

### Lagging
```gauss
// Single lag
x_lag1 = lagn(x, 1);           // Lag 1 period
x_lag4 = lagn(x, 4);           // Lag 4 periods

// Multiple lags at once
lags = lagn(x, 1|2|3);         // Returns Nx3 with lags 1, 2, 3

// Leading (negative lag)
x_lead1 = lagn(x, -1);         // Lead 1 period
```

### Differencing
```gauss
// First difference
dx = x - lagn(x, 1);

// Or use diff function
dx = diff(x, 1);               // First difference
dx = diff(x, 4);               // Fourth difference (e.g., seasonal)

// Log difference (returns/growth rate)
returns = ln(x) - lagn(ln(x), 1);
```

## Frequency Conversion

### tsAggregate (GAUSS 26+)
```gauss
// Convert daily to monthly
monthly = tsAggregate(daily_data, "Monthly", "last");

// Available frequencies:
// "Second", "Minute", "Hourly", "Daily", "Monthly", "Quarterly", "Yearly"
// Or shortcuts: "S", "N", "H", "D", "M", "Q", "Y"

// Available methods:
// "last"    - Last observation in period
// "first"   - First observation in period
// "lastBD"  - Last business day (Mon-Fri)
// "mean"    - Average
// "sum"     - Sum
// "max"     - Maximum
// "min"     - Minimum
// "median"  - Median
// "sd"      - Standard deviation
// "count"   - Count of observations

// Examples
monthly_close = tsAggregate(daily, "Monthly", "last");
monthly_avg = tsAggregate(daily, "Monthly", "mean");
quarterly_sum = tsAggregate(monthly, "Quarterly", "sum");
yearly_max = tsAggregate(daily, "Yearly", "max");
```

## Moving Averages and Smoothing

### Simple Moving Average
```gauss
// Rolling mean
window = 20;
ma = movavg(x, window);

// Manual implementation
ma = zeros(rows(x), 1) + miss();
for i (window, rows(x), 1);
    ma[i] = meanc(x[i-window+1:i]);
endfor;
```

### Exponential Moving Average
```gauss
// EMA with span
alpha = 2 / (span + 1);
ema = zeros(rows(x), 1);
ema[1] = x[1];
for i (2, rows(x), 1);
    ema[i] = alpha * x[i] + (1 - alpha) * ema[i-1];
endfor;
```

### Rolling Statistics
```gauss
// Rolling standard deviation
window = 20;
rolling_std = zeros(rows(x), 1) + miss();
for i (window, rows(x), 1);
    rolling_std[i] = stdc(x[i-window+1:i]);
endfor;

// Rolling correlation
rolling_corr = zeros(rows(x), 1) + miss();
for i (window, rows(x), 1);
    rolling_corr[i] = corrx(x[i-window+1:i] ~ y[i-window+1:i])[1,2];
endfor;
```

## Returns Calculation

### Simple Returns
```gauss
// Period returns
simple_ret = (x - lagn(x, 1)) ./ lagn(x, 1);

// Percent change
pct_change = 100 * simple_ret;
```

### Log Returns
```gauss
// Continuously compounded returns
log_ret = ln(x) - lagn(ln(x), 1);
// Or equivalently:
log_ret = ln(x ./ lagn(x, 1));
```

### Cumulative Returns
```gauss
// From simple returns
cum_ret = exp(cumsumc(log_ret)) - 1;

// Or compound
wealth = cumprodc(1 + simple_ret);
```

## Autocorrelation

### ACF (Autocorrelation Function)
```gauss
// Autocorrelation at lag k
k = 5;
x_c = x - meanc(x);
acf_k = sumc(x_c[1:rows(x)-k] .* x_c[1+k:rows(x)]) / sumc(x_c.^2);

// Multiple lags
maxlag = 20;
acf = zeros(maxlag, 1);
for k (1, maxlag, 1);
    acf[k] = sumc(x_c[1:rows(x)-k] .* x_c[1+k:rows(x)]) / sumc(x_c.^2);
endfor;
```

### PACF (Partial Autocorrelation)
```gauss
// Use Yule-Walker or OLS approach
// For PACF at lag k, regress x on lags 1 through k
```

## Stationarity Tests

### ADF Test (Augmented Dickey-Fuller)
```gauss
// Using TSMT module (if available)
// { tstat, pval } = adf(y, lags, trend);

// Manual ADF
dy = diff(y, 1);
y_lag = lagn(y, 1);
// Include lagged differences for augmentation
// Regress dy on y_lag and lagged dy's
```

## Seasonal Adjustment

### Differencing for Seasonality
```gauss
// Remove seasonal pattern (e.g., monthly data, annual seasonality)
y_seasadj = y - lagn(y, 12);   // First seasonal difference

// Double differencing (trend + seasonal)
y_double = diff(diff(y, 1), 12);
```

### Seasonal Decomposition
```gauss
// STL or moving average decomposition
// Calculate trend with centered moving average
window = 12;  // For monthly data
trend = movavg(y, window);

// Detrended series
detrended = y - trend;

// Seasonal component (average by month)
seasonal = zeros(rows(y), 1);
for m (1, 12, 1);
    mask = month(dates) .== m;
    seasonal[mask .== 1] = meanc(selif(detrended, mask));
endfor;

// Residual
residual = y - trend - seasonal;
```

## Common Patterns

### Creating Trading Calendar
```gauss
// Generate business days only
start = timeutc(2024, 1, 1, 0, 0, 0);
end_date = timeutc(2024, 12, 31, 0, 0, 0);

dates = {};
dt = start;
do while dt <= end_date;
    dow = dayofweek(dt);
    if dow > 1 and dow < 7;  // Mon=2 to Fri=6 (or 1-7 depending on your setup)
        dates = dates | dt;
    endif;
    dt = dt + 86400;
endo;
```

### Aligning Multiple Time Series
```gauss
// Merge two time series on dates
df1 = loadd("series1.csv", "date(Date) + Value1");
df2 = loadd("series2.csv", "date(Date) + Value2");

// Inner join on date
merged = innerjoin(df1, "Date", df2, "Date");
```

### Computing Rolling Volatility
```gauss
// Annualized volatility (assuming daily returns)
window = 20;
ann_factor = sqrt(252);  // Trading days per year

rolling_vol = zeros(rows(returns), 1) + miss();
for i (window, rows(returns), 1);
    rolling_vol[i] = stdc(returns[i-window+1:i]) * ann_factor;
endfor;
```

### Handling Missing Dates
```gauss
// Fill forward (carry last observation)
// Find gaps and fill
filled = x;
for i (2, rows(x), 1);
    if ismiss(filled[i]);
        filled[i] = filled[i-1];
    endif;
endfor;

// Or use packr to remove missing
clean = packr(df);
```

## Time Series Plotting

```gauss
struct plotControl pc;
pc = plotGetDefaults("xy");

// Format x-axis as dates
plotSetXTicLabel(&pc, "%Y-%m");

// Add title and labels
plotSetTitle(&pc, "Stock Price Over Time");
plotSetXLabel(&pc, "Date");
plotSetYLabel(&pc, "Price");

plotXY(pc, dates, prices);
```

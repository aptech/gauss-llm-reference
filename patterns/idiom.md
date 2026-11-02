# GAUSS Idiom

Patterns that make GAUSS code shorter and keep its meaning: variable names,
dates and missing values travel with the data. Each pattern shows the clumsy
version first, then the GAUSS one.

## Keep dataframes; do not strip them

Converting a dataframe to a matrix throws away the column names and any date
column. Everything downstream then prints `X1 X2 X3`.

```gauss
// Clumsy: strip, rebuild, rename
gdp  = asMatrix(raw[., "GDP"]);
cpi  = asMatrix(raw[., "CPI"]);
y    = gdp ~ cpi;
names = "GDP" $| "CPI";

// GAUSS: select and assign by column name
y = raw[., "GDP" "CPI"];
raw[., "CPI"] = 100 * (raw[., "CPI"] - lagn(raw[., "CPI"], 1));
```

Names survive `packr`, `lagn`, `ln`, column assignment and column selection, so
`call dstatmt(y[., "GDP" "CPI"])` prints a labelled table. Multiplying by a
scalar does not: `400 * raw[., "CPI"]` returns a plain matrix. Assign the
result back into a named column, as above, and the name stays.

If the dataframe has a date column and a library function accepts dates (for
example a time series estimator), keep the column in the data you pass.
Selecting only the numeric columns loses the dates.

## Select rows by date with between

A date column compares with date strings directly; `asDate` is not needed.

```gauss
// Clumsy
y = selif(data, data[., "date"] .>= asDate("1960-01-01")
    .and data[., "date"] .< asDate("2020-01-01"));

// GAUSS: "left" keeps 1960-01-01 and leaves out 2020-01-01
y = selif(data, between(data[., "date"], "1960", "2020", "left"));
```

## Date columns print as dates

A date column holds POSIX seconds and a display format. The format only
changes how the values print; arithmetic and comparisons use the same numbers.
`ntos` returns the formatted text, so there is no need to pass format codes to
`posixtostrc`.

```gauss
// Clumsy
print "Sample: " $+ posixtostrc(d[1], "%YQ%q") $+ " to "
    $+ posixtostrc(d[rows(d)], "%YQ%q");

// GAUSS: d is a date column
d = setColDateFormats(d, "%YQ%q", 1);     // print as 1960Q1
print "Sample: " $+ ntos(d[1]) $+ " to " $+ ntos(d[rows(d)]);
```

To make a date column from POSIX numbers, use
`setColTypes(asDF(x, "date"), "date")`, then set the display format with
`setColDateFormats`. `asDate` reads date strings of any year, but on numbers
in GAUSS 27.0.0 it wraps values at or below -2^31 seconds (before 1901-12-13),
so 1871 becomes 2007.

The result of arithmetic on a date column is also a date column, so a
difference of 91 days prints as a date. Use `asMatrix` to print it as a number.

## Use the library, not a loop

| To get | Use | Not |
|--------|-----|-----|
| Mean, standard deviation, min, max, missing count | `call dstatmt(y)` | a `for` loop of `print meanc(...)` |
| Rows without missing values | `packr(y)` | `selif(y, rowcontains(y, miss(0,0)) .== 0)` |
| A previous value | `lagn(x, 1)` | slicing `x[1:n-1]` and padding by hand |
| A statistic the library already computes | the procedure, e.g. `ljungBoxTest(resid, lags=8)` | a loop over `acf` |

`lagn` fills the first rows with missing values, so the result lines up with
the original rows and with any dates.

## Differences and growth rates

Slice-and-pad code is easy to get wrong:

```gauss
// Clumsy
inflation = missrv(zeros(rows(cpi), 1), 0);
inflation[2:rows(cpi)] = 400 * ln(cpi[2:rows(cpi)] ./ cpi[1:rows(cpi)-1]);
inflation[1] = miss(0, 0);

// GAUSS: replace the CPI level with annualized quarterly inflation
raw[., "CPI"] = 400 * diff(ln(raw[., "CPI"]));
```

`diff` keeps the number of rows and leaves the first row missing. To change
a column and drop that row, keep the names with `dfname` and drop the row
with `trimr`:

```gauss
data[., "ffr"] = diff(data[., "ffr"]);
data = dfname(data, "dffr", "ffr");
y = trimr(data, 1, 0);          // diff leaves the first row missing
```

If your GAUSS does not have `diff`, define it once. A procedure can sit after
the final `end;` of a program file:

```gauss
raw[., "CPI"] = 400 * diff(ln(raw[., "CPI"]));
end;

// First difference of each column; the first `lag` rows are missing.
proc (1) = diff(x, lag=1);
    retp(x - lagn(x, lag));
endp;
```

## Pass options as pairs or keywords

Where a function accepts option name/value pairs, give them in the call. Do
not build an options variable one setter call at a time.

```gauss
// Clumsy
opts = fred_set("frequency", "q");
opts = fred_set("aggregation_method", "avg", opts);
opts = fred_set("observation_start", "1960-01-01", opts);
raw = fred_load("GDPC1 + CPIAUCSL", opts);

// GAUSS
raw = fred_load("GDPC1 + CPIAUCSL",
    "frequency", "q", "aggregation_method", "avg",
    "observation_start", "1960-01-01");
```

Procedures you write can take keywords with defaults the same way:
`proc (1) = diff(x, lag=1)`.

Leave out arguments that equal their defaults. `const=1` where the constant
is already the default only makes the reader wonder what changed.

## Program procedures: at the bottom, optional inputs as keywords

In a program file, put your own procedures after the main code, each with a
comment saying what it does. Give optional inputs keyword defaults, using
`{}` for "none", so callers leave them out instead of passing placeholders.
Use the same keyword names as the library procedures they pass through to.

```gauss
// Clumsy: placeholders for unused inputs
report = briefing(panel, {}, {}, "No indicators", "baseline");

// GAUSS
report = briefing(panel, label="No indicators", output_dir="baseline");
...
proc (1) = briefing(panel, xreg={}, xreg_future={}, label="", output_dir="");
```

## Let procedures print their own results

If a procedure prints a result table, use its printout. Do not silence it
with `quiet=1` and rebuild the same table by hand. Keep `quiet=1` for fits
inside loops and for results you do not show.

```gauss
// Clumsy
fc = bvarForecast(fit, 8, levels=0.68, quiet=1);
print sprintf("%-8s%10.3f", ntos(fc.forecast_dates), fc.forecasts);
// ... and another table for the bands

// GAUSS: prints the medians and their 68% bands
fc = bvarForecast(fit, 8, levels=0.68);
```

Never call procedures whose names start with `__` from a program. They are
internal and can change without notice.

## Print tables with sprintf on vectors

`sprintf` takes vectors and returns one formatted line per row, so a table
needs no loop. Use the same widths for the header and the data so the columns
line up.

```gauss
p      = 1:4;                                   // 1:4 is a column vector
log_ml = r1.log_ml | r2.log_ml | r3.log_ml | r4.log_ml;

print sprintf("%8s %12s", "p", "Log ML");
print sprintf("%8d %12.2f", p, log_ml);
```

When an argument is a matrix, `sprintf` reuses the last format for each of
its columns, so a table of any width takes two lines. A row of strings works
the same way for the header. Do not add a `-` rule under the header.

```gauss
print sprintf("%-8s%10s", "Quarter", names');       // names is a column of strings
print sprintf("%-8s%10.3f", quarters, forecasts);   // one %10.3f per column
```

Format numbers in `sprintf` instead of building label strings first. `%g`
drops trailing zeros, so 0.05, 1 and 0.1996 print as written:

```gauss
// Clumsy
labels = { "0.05", "0.1", "1" } $| sprintf("%.4f", chosen);
print sprintf("%-8s%10.3f", labels, log_ml);

// GAUSS
tight = 0.05 | 0.1 | 1 | chosen;
print sprintf("%-8.4g%10.3f", tight, log_ml);
```

Avoid `format` for this. It changes print state for everything that runs
afterwards, including library output, and needs a reset that is easy to skip.
`sprintf` formats only the line you give it.

When a quantity can be astronomically large, print its logarithm. A Bayes
factor of `exp(30.8)` prints as `23117813544885.8`; the log difference, `30.8`,
is readable.

## Braces for constant vectors; `|` and `~` for anything else

A vector of literal numbers is a brace literal. Commas separate rows, spaces
separate columns.

```gauss
prior_centers = { 0, 1, 1, 1 };     // 4x1 column
fc = bvarForecast(fit, 8, levels={ 0.68, 0.90 });
```

Braces accept literal numbers only. Variables and structure members inside
braces give `+DEN` with no error, so build those vectors with `|` and `~`:

```gauss
a = 7;  b = 8;

x = { a, b };       // WRONG: prints +DEN for each element, no error
x = a | b;          // 7 over 8 (a column)
x = a ~ b;          // 7 beside 8 (a row)
log_ml = r1.log_ml | r2.log_ml;
```

A constant string table is a brace literal passed inline, `names={ "VAR",
"BVAR" }`, or declared at the top level with `string names = { "gdp", "cons" };`.
A bare `x = { "a", "b" };` is an old-style character matrix. Inside a `proc`,
`string x = { ... };` does not compile; pass the literal inline or use `$|`.

## Refer to columns by name, not by position

```gauss
gdp = fc.forecasts[., "gdp"];          // not fc.forecasts[., 1]
```

When a result packs several blocks into one row, reshape it into a table
with one row per variable instead of indexing column ranges such as `22:28`:

```gauss
crps = reshape(ev.mean_crps[h, .], n_models, n_vars)';   // variables x models
rel = crps[., 1:3] ./ crps[., n_models];
```

## One argument per line when a call does not fit

When a call does not fit in 88 characters, put each argument on its own line
and the closing parenthesis on a line of its own:

```gauss
fit = bvarFit(
    y,
    p=4,
    lag1_prior_mean=prior_centers,
    overall_tightness=0.2,
    quiet=1
);
```

## Do not hide GAUSS functions

A variable named `ols`, `dummy` or `diff` hides the GAUSS procedure of that
name for the rest of the program. Use names such as `ols_fit`.

## Rename columns with dfname(df, new, old)

The new name comes first:

```gauss
df = dfname(df, "GDP", "GDPC1");     // GDPC1 becomes GDP
```

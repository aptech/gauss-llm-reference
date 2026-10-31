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

## Use the library, not a loop

| To get | Use | Not |
|--------|-----|-----|
| Mean, standard deviation, min, max, missing count | `call dstatmt(y)` | a `for` loop of `print meanc(...)` |
| Rows without missing values | `packr(y)` | `selif(y, rowcontains(y, miss(0,0)) .== 0)` |
| A previous value | `lagn(x, 1)` | slicing `x[1:n-1]` and padding by hand |

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

Avoid `format` for this. It changes print state for everything that runs
afterwards, including library output, and needs a reset that is easy to skip.
`sprintf` formats only the line you give it.

When a quantity can be astronomically large, print its logarithm. A Bayes
factor of `exp(30.8)` prints as `23117813544885.8`; the log difference, `30.8`,
is readable.

## Build vectors with `|` and `~`, not braces

Braces accept literal numbers only. Variables and structure members inside
braces give `+DEN` with no error.

```gauss
a = 7;  b = 8;

x = { a, b };       // WRONG: prints +DEN for each element, no error
x = a | b;          // 7 over 8 (a column)
x = a ~ b;          // 7 beside 8 (a row)
x = { 7, 8 };       // fine: literals
```

## Rename columns with dfname(df, new, old)

The new name comes first:

```gauss
df = dfname(df, "GDP", "GDPC1");     // GDPC1 becomes GDP
```

# GAUSS Programming Language Reference

This reference helps AI assistants (Claude, ChatGPT, etc.) write correct, idiomatic GAUSS code.

**GAUSS** is a matrix-oriented programming language for statistical analysis, econometrics, and data science, developed by Aptech Systems.

---

## Critical Gotchas (Read First!)

### 1. Matrix vs Element-wise Operations

| Operation | Matrix-wide | Element-wise |
|-----------|-------------|--------------|
| Multiply | `*` | `.*` |
| Divide | `/` | `./` |
| Power | `^` | `.^` |
| Equal | `==` (scalar result) | `.==` (mask) |
| Less than | `<` (scalar result) | `.<` (mask) |

```gauss
// WRONG - this is matrix multiply
c = a * b;

// RIGHT - element-wise multiply
c = a .* b;
```

### 2. String Operators Use $

```gauss
// WRONG
s = "hello" + "world";

// RIGHT
s = "hello" $+ "world";    // Combine: "helloworld"
names = "A" $| "B" $| "C"; // Column vector (for column names)
names = "A" $~ "B" $~ "C"; // Row vector
```

### 3. 1-Based Indexing

```gauss
// GAUSS is 1-indexed, not 0-indexed
first = x[1, 1];           // First element
last = x[rows(x), cols(x)]; // Last element
```

### 4. Boolean Selection Uses selif()

```gauss
// WRONG (Python-style)
subset = x[x .> 0];

// RIGHT (GAUSS-style)
subset = selif(x, x .> 0);
```

### 5. Semicolons Required

```gauss
x = 5;           // Semicolon required
y = x + 1;       // On every statement
```

### 6. `local` Only Inside Procedures

```gauss
// At global scope - just assign, no declaration
x = { 1, 2, 3 };

// Inside procedures - use local
proc (1) = myFunc(x);
    local a, b;        // Declare locals at top
    a = x + 1;
    b = a * 2;
    retp(b);
endp;
```

### 7. Logical Operators

| Operator | Type | Returns |
|----------|------|---------|
| `and` | Matrix-wide | Scalar (1 if both all non-zero) |
| `or` | Matrix-wide | Scalar |
| `.and` | Element-wise | 0/1 matrix |
| `.or` | Element-wise | 0/1 matrix |

```gauss
// For row-by-row filtering, use element-wise:
subset = selif(data, (data[.,"Age"] .> 18) .and (data[.,"Income"] .> 50000));
```

---

## Quick Syntax Reference

### Matrix Creation

```gauss
x = { 1 2 3, 4 5 6 };     // 2x3 matrix (comma separates rows)
x = zeros(3, 4);           // 3x4 zeros
x = ones(3, 4);            // 3x4 ones
x = eye(3);                // 3x3 identity
x = rndn(100, 5);          // 100x5 random normal
x = seqa(1, 1, 10);        // Sequence: 1, 2, ..., 10
x = 1:10;                  // Same as seqa(1, 1, 10)
```

### Indexing

```gauss
x[1, .]           // First row
x[., 2]           // Second column
x[1:3, .]         // Rows 1-3
x[., 2:4]         // Columns 2-4
x[2, 3]           // Element at row 2, col 3

// Dataframes by column name
df[., "Age"]              // Single column
df[., "Age" "Income"]     // Multiple columns (space-separated)
```

### Control Flow

```gauss
// If statement
if x > 0;
    y = 1;
elseif x < 0;
    y = -1;
else;
    y = 0;
endif;

// For loop
for i (1, 10, 1);
    print i;
endfor;

// While loop
do while i < 10;
    i = i + 1;
endo;
```

### Procedures (Functions)

```gauss
// Single return value
proc (1) = double(x);
    retp(x * 2);
endp;

// Multiple return values
proc (2) = stats(x);
    local m, s;
    m = meanc(x);
    s = stdc(x);
    retp(m, s);
endp;

// Call with multiple returns
{ mean_val, std_val } = stats(data);
```

### Common Functions

```gauss
// Statistics (column-wise)
meanc(x)          // Column means
stdc(x)           // Column std dev
sumc(x)           // Column sums
minc(x)           // Column minimums
maxc(x)           // Column maximums

// Row-wise versions
meanr(x)          // Row means
sumr(x)           // Row sums

// Matrix operations
rows(x)           // Number of rows
cols(x)           // Number of columns
x'                // Transpose
inv(x)            // Inverse
det(x)            // Determinant

// Data I/O
data = loadd("file.csv");
saved(data, "output.csv");
```

### Dataframe Operations

```gauss
// Create
df = asdf(matrix_data, "Col1" $| "Col2" $| "Col3");
df = loadd("data.csv");

// Select/filter
subset = df[., "Age" "Income"];
filtered = selif(df, df[., "Age"] .> 18);

// Info
head(df);
getColNames(df);
rows(df);

// Missing values
df = packr(df);            // Remove rows with missing
df = impute(df, "mean");   // Fill with column means
```

---

## Common Patterns

### Data Cleaning Pipeline

```gauss
// Load
data = loadd("raw.csv");

// Preview
print "Shape:" rows(data) "x" cols(data);
head(data);

// Remove missing
data = packr(data);

// Filter
data = selif(data, data[., "Age"] .> 0);
```

### OLS Regression

```gauss
// Quick OLS
y = data[., "y"];
X = ones(rows(data), 1) ~ data[., "x1" "x2"];  // Add constant
b = y / X;           // Coefficients

// With olsmt for full output
struct olsmtControl ctl;
ctl = olsmtControlCreate();
struct olsmtOut out;
out = olsmt("", y ~ x1 + x2, ctl);
```

### Time Series Prep

```gauss
// Load with date
df = loadd("prices.csv", "date(Date) + Price");

// Sort by date
df = sortc(df, "Date");

// Create lags
price = df[., "Price"];
lag1 = lagn(price, 1);
lag2 = lagn(price, 2);

// Remove missing from lags
df = packr(df ~ asdf(lag1, "Lag1") ~ asdf(lag2, "Lag2"));
```

---

## Detailed Reference Files

| Topic | File |
|-------|------|
| **Gotchas** | |
| Operators | `gotchas/operators.md` |
| Indexing | `gotchas/indexing.md` |
| Strings | `gotchas/strings.md` |
| Variable scope | `gotchas/variable-scope.md` |
| Missing values | `gotchas/missing-values.md` |
| Common errors | `gotchas/common-errors.md` |
| **Language** | |
| Matrices | `language/matrices.md` |
| Dataframes | `language/dataframes.md` |
| Strings | `language/strings.md` |
| Structures | `language/structures.md` |
| Time series | `language/timeseries.md` |
| Panel data | `language/panel.md` |
| Graphics | `language/graphics.md` |
| I/O | `language/io.md` |
| **Translation** | |
| From Python | `vs-other-languages/from-python.md` |
| **Apps** | |
| TSMT | `apps/tsmt.md` |
| GARCH | `apps/garch.md` |

---

## vs Python/NumPy Quick Reference

| Python | GAUSS |
|--------|-------|
| `a @ b` | `a * b` (matrix multiply) |
| `a * b` | `a .* b` (element-wise) |
| `a[0]` | `a[1]` (1-indexed) |
| `a[mask]` | `selif(a, mask)` |
| `"a" + "b"` | `"a" $+ "b"` |
| `def f(x): return x` | `proc (1) = f(x); retp(x); endp;` |

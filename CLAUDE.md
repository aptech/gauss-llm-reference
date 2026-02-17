# GAUSS Programming Language Reference

This reference helps Claude write idiomatic GAUSS code. GAUSS is a matrix-oriented programming language designed for statistical analysis, econometrics, and data science.

## Quick Reference

### Basic Operators

```gauss
// Arithmetic (element-wise by default)
a + b       // addition
a - b       // subtraction
a * b       // matrix multiplication (NOT element-wise)
a .* b      // element-wise multiplication
a / b       // matrix division (b^-1 * a)
a ./ b      // element-wise division
a ^ 2       // matrix power
a .^ 2      // element-wise power

// Comparison (element-wise, return 0/1 matrix)
a .== b     // equal (element-wise)
a .!= b     // not equal (element-wise)
a .< b      // less than
a .<= b     // less than or equal
a .> b      // greater than
a .>= b     // greater than or equal

// Comparison (matrix-wide, return scalar 1 or 0)
a == b      // 1 if ALL elements equal, 0 otherwise
a != b      // 1 if ALL elements differ, 0 otherwise

// Logical
a and b     // logical AND
a or b      // logical OR
not a       // logical NOT

// String operators
a $+ b      // string combine (merges into single string)
a $~ b      // string horizontal concatenation (creates columns)
a $| b      // string vertical concatenation (creates rows)
```

### Matrix Creation

```gauss
// Numeric matrices
x = { 1 2 3, 4 5 6 };           // 2x3 matrix (commas separate rows)
x = zeros(3, 4);                 // 3x4 matrix of zeros
x = ones(3, 4);                  // 3x4 matrix of ones
x = eye(3);                      // 3x3 identity matrix
x = rndn(100, 5);                // 100x5 random normal
x = rndu(100, 5);                // 100x5 random uniform [0,1)
x = seqa(1, 1, 10);              // sequence: 1, 2, ..., 10
x = seqa(0, 0.5, 5);             // sequence: 0, 0.5, 1, 1.5, 2

// String arrays
s = "hello";                     // string
s = "a" $| "b" $| "c";           // 3x1 string array (vertical concat)
s = "a" $~ "b" $~ "c";           // 1x3 string array (horizontal concat)
s = "a" $+ "b";                  // "ab" (string combine)
string s = { "a" "b", "c" "d", "e" "f" }; // 3x2 string array
```

### Matrix Indexing

```gauss
x = rndn(5, 3);

// Row/column selection
x[1, .]         // first row, all columns
x[., 2]         // all rows, second column
x[1:3, .]       // rows 1-3, all columns
x[., 2:3]       // all rows, columns 2-3
x[1, 2]         // single element

// Boolean/conditional selection (use selif, not direct indexing)
selif(x, x[., 1] .> 0)       // rows where column 1 > 0
delif(x, x[., 1] .< 0)       // delete rows where column 1 < 0
indexcat(x[., 1], x[., 1] .> 0)  // get row indices where condition is true

// Dataframe column selection by name
df[., "Age"]                    // single column
df[., "Age" "Income"]           // multiple columns (space-separated)
df[., "Age":"Zip"]              // column range
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
for i (1, 10, 1);      // i from 1 to 10, step 1
    print i;
endfor;

// While loop
i = 1;
do while i <= 10;
    print i;
    i = i + 1;
endo;

// Do until loop
i = 1;
do until i > 10;
    print i;
    i = i + 1;
endo;
```

### Procedures (Functions)

```gauss
// Basic procedure
proc (1) = myMean(x);
    local m;              // declare ALL locals at top of proc
    m = meanc(x);
    retp(m);
endp;

// Local variable rules:
// 1. Only valid inside procs (not at global scope)
// 2. Scoped to ENTIRE proc, not to blocks (even if declared in a block)
// 3. Declare each local only ONCE per proc

// OK: declaring local inside a block (but it's proc-scoped)
proc (1) = okExample(x);
    local i;
    for i (1, 10, 1);
        local temp;       // OK, but temp is scoped to entire proc
        temp = x[i];
    endfor;
    print temp;           // works - temp is still in scope
    retp(temp);
endp;

// WRONG: declaring same local twice
proc (1) = badExample(x);
    local i;
    for i (1, 10, 1);
        local temp;
        temp = x[i];
    endfor;

    local temp;           // WRONG: temp already declared above
    retp(x);
endp;

// BEST PRACTICE: declare all locals at top for clarity
proc (1) = bestExample(x);
    local i, temp, result;    // all locals at top

    for i (1, 10, 1);
        temp = x[i];
    endfor;

    if x > 0;
        result = sqrt(x);
    endif;

    retp(result);
endp;

// Multiple return values
proc (2) = myStats(x);
    local m, s;
    m = meanc(x);
    s = stdc(x);
    retp(m, s);
endp;

// Call with multiple returns
{ avg, sd } = myStats(data);

  // Optional arguments pattern
  proc (1) = myFunc(x, ...);
      local opt1, opt2;
      { opt1, opt2 } = dynargsGet(1|2, 1, "default");  // indices, then defaults
      
      // rest of code
      
      retp(result);
  endp;

  // Calling:
  myFunc(x);                    // opt1=1, opt2="default"
  myFunc(x, 5);                 // opt1=5, opt2="default"
  myFunc(x, 5, "custom");       // opt1=5, opt2="custom"

  // Dynamic argument functions:
  dynargsCount()    // Number of optional args passed
  dynargsTypes()    // Vector of type codes for each arg
  dynargsGet(1, default)        // Get 1st optional arg with default
  dynargsGet(1|2|3, d1, d2, d3) // Get multiple with defaults

  // Type codes (from dynargsTypes):
  //   6=matrix  13=string  15=string array  17=struct  21=array  23=struct pointer  38=sparse

  That covers: the pattern, call examples, all three dynargs functions, and type codes as a quick
  reference comment. Compact but complete.
```

### Structures

```gauss
// Define structure
struct mySettings {
    scalar alpha;
    scalar maxIters;
    string method;
    matrix startVals;
};

// Create and use
struct mySettings s;
s.alpha = 0.05;
s.maxIters = 100;
s.method = "BFGS";
s.startVals = zeros(5, 1);

// Pass to procedure
proc (1) = optimize(data, struct mySettings s);
    // use s.alpha, s.maxIters, etc.
endp;
```

See `.claude/gauss/structures.md` for control structures (olsmt, glm, etc.)

### Loading and Saving Data

```gauss
// Load data (auto-detects format: CSV, Excel, Stata, SAS, HDF5)
data = loadd("mydata.csv");
data = loadd("mydata.xlsx");
data = loadd("mydata.dta");

// Load specific columns with formula string
data = loadd("mydata.csv", "Income + Age + Gender");

// Load all except some columns
data = loadd("mydata.csv", ". - ID - Timestamp");

// Load with type specification
data = loadd("mydata.csv", "date(Date) + cat(Region) + Age");

// Save data
saved(data, "output.csv");
saved(data, "output.xlsx");
saved(data, "output.gdat");  // GAUSS native format
```

### Dataframes

```gauss
// Create dataframe from matrix
df = asdf(matrix_data, "col1" $| "col2" $| "col3");

// Column operations
df = df[., "Age" "Income"];             // select columns
head(df);                                // first 5 rows
tail(df);                                // last 5 rows

// Filter rows
young = selif(df, df[., "Age"] .< 30);

// Dataframe info
rows(df);                                // number of rows
cols(df);                                // number of columns
getColNames(df);                         // column names
getColTypes(df);                         // column types (number, string, date, category)

// Aggregation
result = aggregate(df, "mean", "group_col");
result = aggregate(df, "sum", "col1" $| "col2");  // multiple group columns
```

See `.claude/gauss/dataframes.md` for comprehensive dataframe operations.

### Print Statement

```gauss
// Basic printing - space-separated items
print x;                        // print variable
print "Hello";                  // print string
print "Value:" x;               // string followed by variable
print "x=" x "y=" y;            // multiple items

// Print multiple variables
print x y z;                    // prints x, y, z with spaces

// Print matrix with label
print "Results:";
print results;

// Print formatting with format statement
format /rd 10,4;                // 10 wide, 4 decimal places
print x;
format /rd 1,0;                 // reset to defaults

// Format specifiers
format /rd 8,2;                 // right-justify, decimal, 8 wide, 2 decimals
format /ld 8,2;                 // left-justify, decimal
format /re 12,4;                // right-justify, exponential notation
format /ro 8,2;                 // right-justify, overflow stars if too wide

// Suppress line break (print continuation)
print "Part 1";;                // ;; suppresses newline
print " Part 2";                // continues on same line
// Output: "Part 1 Part 2"

// Print to string (sprintf equivalent)
s = sprintf("%10.4f", x);       // formatted string
s = sprintf("Name: %s, Value: %g", name, val);

// Common format patterns
format /rd 12,6;                // for doubles/floats
format /rd 8,0;                 // for integers
format /rd 1,0;                 // compact (minimal spacing)

// ftos - format number to string
s = ftos(x, "%10.4f");          // like sprintf for single number
s = ftos(x, "%*.*lf", 10, 4);   // same with width/precision args
```

**Print gotchas:**
```gauss
// WRONG: comma-separated items
print "x=", x;                  // ERROR - no commas

// WRONG: concatenation in print
print "x=" $+ ftos(x, "%lf");   // Works but verbose

// RIGHT: space-separated
print "x=" x;                   // Simple and correct

// WRONG: using ;; between separate print statements for complex logic
if cond;
    print "yes";;
endif;
print "done";                   // ;; doesn't work across statements

// RIGHT: build string first for complex conditional output
local msg;
msg = "";
if cond;
    msg = "yes ";
endif;
msg = msg $+ "done";
print msg;
```

### Common Statistical Functions

```gauss
// Descriptive statistics
meanc(x)        // column means
stdc(x)         // column std deviations
minc(x)         // column minimums
maxc(x)         // column maximums
sumc(x)         // column sums
prodc(x)        // column products
median(x)       // median (whole matrix)

// Matrix operations
x'              // transpose
inv(x)          // inverse
invpd(x)        // inverse for positive definite matrix
det(x)          // determinant
rank(x)         // rank
eig(x)          // eigenvalues
svd(x)          // singular value decomposition

// Linear algebra
y = x * b;              // matrix multiply
b = y / x;              // solve y = x * b for b
b = inv(x'x) * x'y;     // OLS the hard way
b = olsqr(y, x);        // OLS the easy way

// Efficient determinant
L = chol(X);
d = detl;   // grab determinant computed during chol call
```

### Graphics (Basic)

```gauss
// Scatter plot
plotScatter(x, y);

// Line plot
plotXY(x, y);

// Histogram
plotHist(x, 20);    // 20 bins

// With customization
struct plotControl pc;
pc = plotGetDefaults("scatter");
plotSetTitle(&pc, "My Title");
plotSetXLabel(&pc, "X Variable");
plotSetYLabel(&pc, "Y Variable");
plotScatter(pc, x, y);
```

See `.claude/gauss/graphics.md` for comprehensive graphics reference.

### Common Patterns

#### Reading and Cleaning Data
```gauss
// Load and preview
data = loadd("mydata.csv");
head(data);
rows(data);
getColNames(data);

// Handle missing values
data = packr(data);              // remove rows with any missing
data = impute(data, "mean");     // fill missing with column mean

// Filter data
subset = selif(data, data[., "Age"] .>= 18);
```

#### Regression Analysis
```gauss
// Quick OLS
{ b, se, tstat, pval } = olsqr2(y, x);

// Full OLS with diagnostics
struct olsmtControl ctl;
ctl = olsmtControlCreate();
struct olsmtOut out;
out = olsmt("", y ~ x1 + x2 + x3, ctl);

// Print results
print out.beta;
print out.stderr;
```

#### Panel Data
```gauss
// Check if balanced
pdIsBalanced(panel);

// Create lags by group
panel_lagged = pdLag(panel, 1);

// Difference by group
panel_diff = pdDiff(panel, 1);

// Panel summary statistics
pdSummary(panel);
```

### GAUSS vs Other Languages

| Operation | GAUSS | Python/NumPy | R | MATLAB |
|-----------|-------|--------------|---|--------|
| Matrix multiply | `a * b` | `a @ b` | `a %*% b` | `a * b` |
| Element-wise multiply | `a .* b` | `a * b` | `a * b` | `a .* b` |
| Boolean indexing | `selif(x, mask)` | `x[mask]` | `x[mask,]` | `x(mask,:)` |
| String concat | `a $+ b` | `a + b` | `paste0(a,b)` | `strcat(a,b)` |
| Array indexing | 1-based | 0-based | 1-based | 1-based |
| End statement | `;` required | newline | newline | `;` optional |
| Column vector | `{1,2,3}` | `[[1],[2],[3]]` | `c(1,2,3)` | `[1;2;3]` |
| Row vector | `{1 2 3}` | `[1,2,3]` | `t(c(1,2,3))` | `[1 2 3]` |
| Inline column vector | `1\|2\|3` | `np.array([1,2,3])` | `c(1,2,3)` | `[1;2;3]` |
| Inline row vector | `1~2~3` | `[1,2,3]` | `t(c(1,2,3))` | `[1 2 3]` |
| Sequence 1 to n | `seqa(1,1,n)` | `range(1,n+1)` | `1:n` | `1:n` |
| Logical AND | `a and b` or `.and` | `a & b` | `a & b` | `a & b` |
| Logical OR | `a or b` or `.or` | `a \| b` | `a \| b` | `a \| b` |
| Not equal (element-wise) | `.!=` | `!=` | `!=` | `~=` |
| Not equal (matrix) | `!=` | n/a | n/a | n/a |
| Comments | `//` or `/* */` | `#` | `#` | `%` |
| Function def | `proc (n) = f(x);` | `def f(x):` | `f <- function(x)` | `function y = f(x)` |
| Return value | `retp(x)` | `return x` | `return(x)` | `y = x` (implicit) |

**Key differences from Python/NumPy:**
- `*` is matrix multiply in GAUSS, element-wise in Python
- Use `selif()` not `x[condition]` for boolean selection
- Indices start at 1, not 0
- Semicolons required at end of statements
- String operators use `$` prefix: `$+`, `$|`, `$~`, `.$==`

**Key differences from MATLAB:**
- String operators differ: `$+` (GAUSS) vs `strcat` (MATLAB)
- `!=` comparison is `.!=` in GAUSS
- Procedures use `proc`/`endp` not `function`/`end`
- Return with `retp()` not implicit assignment

### Gotchas and Common Mistakes

```gauss
// WRONG: * is matrix multiply, not element-wise
a * b               // matrix multiplication
a .* b              // element-wise (probably what you want)

// WRONG: = in conditions
if x = 5;           // WRONG: this assigns 5 to x
if x == 5;          // RIGHT: comparison

// WRONG: forgetting semicolons
x = 5               // ERROR
x = 5;              // RIGHT

// WRONG: string concat with +
"a" + "b"           // ERROR
"a" $+ "b"          // RIGHT: "ab"

// WRONG: row vector when column needed for string array
"a" $+ "b" $+ "c"   // 1x1 string "abc"
"a" $| "b" $| "c"   // 3x1 string array

// WRONG: 1-indexed (GAUSS is 1-indexed, not 0-indexed)
x[0, 1]             // ERROR
x[1, 1]             // RIGHT: first element

// WRONG: == vs .== confusion
a == b              // Matrix comparison: scalar 1 if ALL equal
a .== b             // Element-wise: returns 0/1 matrix (mask)
// Use .== when you want a mask for selif()

// WRONG: colon range syntax (not supported)
x = 1:8;            // ERROR - not valid GAUSS
x = seqa(1, 1, 8);  // RIGHT: creates 1, 2, 3, ..., 8
// Note: 1:8 only works INSIDE index brackets: x[1:8, .]

// WRONG: curly braces don't work inline with functions
y = sumc({1,2,3});  // ERROR - can't use braces inline
y = sumc(1|2|3);    // RIGHT: use | for vertical concat
y = sumr(1~2~3);    // RIGHT: use ~ for horizontal concat
```

### Topic-Specific References

- `.claude/gauss/dataframes.md` - Dataframe operations, formula strings, types
- `.claude/gauss/structures.md` - Control structures for olsmt, glm, estimation
- `.claude/gauss/strings.md` - String manipulation and formatting
- `.claude/gauss/graphics.md` - Plotting and visualization
- `.claude/gauss/io.md` - File I/O, databases, web data
- `.claude/gauss/matrices.md` - Matrix operations and linear algebra
- `.claude/gauss/timeseries.md` - Time series analysis
- `.claude/gauss/panel.md` - Panel data operations

### Application Modules

- `.claude/gauss/apps/tsmt.md` - Time Series MT
- `.claude/gauss/apps/fanpac.md` - FANPAC (Factor Analysis)
- `.claude/gauss/apps/cointegration.md` - Cointegration analysis
- `.claude/gauss/apps/garch.md` - GARCH modeling

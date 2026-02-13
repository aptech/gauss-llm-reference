# GAUSS Matrices Reference

## Matrix Creation

### Basic Creation
```gauss
// Direct creation with braces (comma separates rows)
x = { 1 2 3, 4 5 6, 7 8 9 };  // 3x3 matrix

// Row vector
r = { 1 2 3 4 5 };            // 1x5

// Column vector
c = { 1, 2, 3, 4, 5 };        // 5x1
```

### Special Matrices
```gauss
// Zeros and ones
z = zeros(3, 4);              // 3x4 matrix of zeros
o = ones(5, 2);               // 5x2 matrix of ones

// Identity matrix
I = eye(4);                   // 4x4 identity

// Diagonal matrix
d = diagrv(zeros(3, 3), { 1, 2, 3 });  // Diagonal with 1,2,3

// From diagonal vector
d = diag({ 1, 2, 3 });        // 3x3 diagonal matrix
```

### Sequences
```gauss
// Arithmetic sequence
x = seqa(1, 1, 10);           // 1, 2, 3, ..., 10
x = seqa(0, 0.5, 11);         // 0, 0.5, 1, ..., 5
x = seqa(10, -1, 10);         // 10, 9, 8, ..., 1

// Log-spaced sequence
x = seqm(1, 10, 5);           // 5 points from 1 to 10 (log scale)
```

### Random Matrices
```gauss
// Normal (Gaussian) random
x = rndn(100, 5);             // 100x5 standard normal

// Uniform random [0, 1)
x = rndu(100, 5);             // 100x5 uniform

// Bernoulli (0/1)
x = rndbern(100, 1, 0.5);     // 100x1, p=0.5

// Poisson
x = rndpoisson(100, 1, 5);    // 100x1, lambda=5

// Custom distribution
x = rndn(100, 1)*2 + 5;       // Normal with mean=5, sd=2
```

## Matrix Dimensions

```gauss
x = rndn(100, 5);

r = rows(x);                  // 100
c = cols(x);                  // 5
n = cols(x) * rows(x);        // 500 (total elements)

// Check if scalar
isScalar = rows(x) == 1 and cols(x) == 1;

// Check if vector
isVector = rows(x) == 1 or cols(x) == 1;
```

## Indexing and Selection

### Basic Indexing
```gauss
x = rndn(5, 3);

// Single element (1-indexed)
elem = x[2, 3];               // Row 2, column 3

// Entire row/column
row1 = x[1, .];               // First row (1x3)
col2 = x[., 2];               // Second column (5x1)

// Ranges
submat = x[1:3, .];           // Rows 1-3, all columns
submat = x[., 2:3];           // All rows, columns 2-3
submat = x[2:4, 1:2];         // Rows 2-4, columns 1-2

// Last row/column
lastrow = x[rows(x), .];
lastcol = x[., cols(x)];
```

### Advanced Indexing
```gauss
// Index vector selection
idx = { 1, 3, 5 };
selected = x[idx, .];         // Rows 1, 3, 5

// Boolean indexing (returns vector)
mask = x[., 1] .> 0;          // Boolean mask
positive = selif(x, mask);    // Rows where col 1 > 0

// Find indices where condition is true
idx = indexcat(x[., 1], x[., 1] .> 0);
```

## Matrix Concatenation

```gauss
a = ones(2, 3);
b = zeros(2, 3);
c = eye(3);

// Vertical concatenation (stack rows)
v = a | b;                    // 4x3

// Horizontal concatenation (add columns)
h = a ~ a;                    // 2x6

// Mixed
m = (a | b) ~ (a | b);        // 4x6
```

## Matrix Operations

### Arithmetic
```gauss
// Matrix multiplication (NOT element-wise)
c = a * b;                    // Matrix multiply (a cols must = b rows)

// Element-wise operations
c = a .* b;                   // Element-wise multiply
c = a ./ b;                   // Element-wise divide
c = a .^ 2;                   // Element-wise power

// Matrix power
c = a ^ 2;                    // a * a (matrix multiply)

// Division (solve linear system)
x = b / a;                    // Solves a*x = b for x
```

### Transpose and Reshape
```gauss
// Transpose
t = x';

// Reshape (fills by column)
x = seqa(1, 1, 12);
m = reshape(x, 3, 4);         // 3x4 matrix

// Vector extraction (column-major)
v = vec(m);                   // Vectorize matrix to column

// Flip
f = rev(x);                   // Reverse rows
f = rev(x');                  // Reverse columns (transpose, rev, transpose)
```

### Comparison
```gauss
// Element-wise comparison (returns 0/1 matrix)
c = a .== b;                  // Equal
c = a .!= b;                  // Not equal
c = a .< b;                   // Less than
c = a .<= b;                  // Less or equal
c = a .> b;                   // Greater than
c = a .>= b;                  // Greater or equal

// All/any checks
allPositive = sumc(sumc(x .> 0)) == rows(x)*cols(x);
anyNegative = sumc(sumc(x .< 0)) > 0;
```

## Statistical Functions

### Column-wise (most common)
```gauss
x = rndn(100, 5);

// Basic statistics
m = meanc(x);                 // Column means (5x1)
s = stdc(x);                  // Column std devs
v = varc(x);                  // Column variances
mn = minc(x);                 // Column minimums
mx = maxc(x);                 // Column maximums
sm = sumc(x);                 // Column sums
pd = prodc(x);                // Column products

// Cumulative
cs = cumsumc(x);              // Cumulative sum (by column)
cp = cumprodc(x);             // Cumulative product
```

### Row-wise
```gauss
// Add 'r' for row operations
m = meanr(x);                 // Row means (100x1)
s = sumr(x);                  // Row sums
```

### Whole Matrix
```gauss
// Median (entire matrix)
med = median(x);

// Percentiles
p25 = quantile(x, 0.25);
p75 = quantile(x, 0.75);
```

## Linear Algebra

### Basic Operations
```gauss
a = rndn(4, 4);

// Determinant
d = det(a);

// Inverse
ai = inv(a);

// Verify: a * inv(a) should be identity
check = a * ai;               // Should be eye(4)

// Pseudo-inverse (for non-square or singular)
pi = pinv(a);
```

### Rank and Condition
```gauss
r = rank(a);                  // Matrix rank
c = cond(a);                  // Condition number
```

### Eigenvalues and Eigenvectors
```gauss
// Eigenvalues only
lambda = eig(a);

// Eigenvalues and eigenvectors
{ lambda, V } = eigv(a);
// a * V = V * diag(lambda)

// For symmetric matrices (faster)
{ lambda, V } = eigrs(a);     // Real symmetric
```

### Singular Value Decomposition
```gauss
{ u, s, v } = svd(a);
// a = u * diag(s) * v'

// Compact form
{ u, s, v } = svd1(a);
```

### Cholesky Decomposition
```gauss
// For positive definite matrices
L = chol(a);                  // a = L'L (upper triangular L')
L = cholup(a);                // a = LL' (lower triangular L)
```

### QR Decomposition
```gauss
{ q, r } = qr(a);
// a = q * r
```

### Solving Linear Systems
```gauss
// Solve Ax = b for x
a = rndn(3, 3);
b = rndn(3, 1);

x = b / a;                    // General solution
x = inv(a) * b;               // Same (less efficient)

// For positive definite A
x = cholsol(a, b);            // Using Cholesky

// Least squares (over/underdetermined)
x = olsqr(b, a);              // b = a*x + error
```

## Matrix Manipulation

### Sorting
```gauss
// Sort by column
sorted = sortc(x, 1);         // Sort by column 1, ascending
sorted = sortc(x, 1, -1);     // Descending

// Get sort indices
idx = sortindc(x[., 1], 1);   // Indices for ascending sort
sorted = x[idx, .];
```

### Unique Values
```gauss
u = unique(x);                // Unique values
u = unique(x[., 1]);          // Unique in column 1
```

### Deleting Rows/Columns
```gauss
// Delete rows
x = delrows(x, 3);            // Delete row 3
x = delrows(x, 1|3|5);        // Delete rows 1, 3, 5

// Delete columns
x = delcols(x, 2);            // Delete column 2

// Delete by condition
x = delif(x, x[., 1] .< 0);   // Delete where col 1 < 0
```

### Missing Values
```gauss
// Check for missing
hasMiss = ismiss(x);          // 1 if any missing

// Mask of missings
mask = x .== miss();

// Note: miss == miss returns 1 (true) in GAUSS by default (configurable)
// So indexcat(x, miss(1,1)) works to find missing value indices

// Remove rows with missing
clean = packr(x);

// Replace missing
x = missrv(x, 0);             // Replace with 0
x = missrv(x, meanc(packr(x))); // Replace with column mean
```

## Common Patterns

### Standardization
```gauss
// Z-score standardization
mu = meanc(x);
sigma = stdc(x);
z = (x - mu') ./ sigma';

// Min-max scaling to [0, 1]
mn = minc(x);
mx = maxc(x);
scaled = (x - mn') ./ (mx' - mn');
```

### Covariance and Correlation
```gauss
// Variance-covariance matrix
vcov = varCovX(x);            // Or compute manually:
n = rows(x);
mu = meanc(x);
xc = x - mu';
vcov = (xc'xc) / (n-1);

// Correlation matrix
corr = corrx(x);
```

### Matrix Norms
```gauss
// Frobenius norm
fnorm = sqrt(sumc(sumc(x .^ 2)));

// Maximum absolute column sum (1-norm)
norm1 = maxc(sumc(abs(x)));

// Maximum absolute row sum (infinity norm)
norminf = maxc(sumr(abs(x)));
```

### Kronecker Product
```gauss
k = a .*. b;                  // Kronecker product
```

### Trace
```gauss
tr = sumc(diag(a));           // Sum of diagonal elements
```

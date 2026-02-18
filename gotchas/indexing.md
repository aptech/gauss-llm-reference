# Indexing Gotchas

## 1-Based Indexing

GAUSS is 1-indexed (like R, MATLAB), not 0-indexed (like Python).

```gauss
first = x[1, 1];    // First row, first column
last = x[rows(x), cols(x)];  // Last element
```

Note: `0` in indexing means "all" (same as `.`):
```gauss
x[0, 1]             // All rows, column 1 - same as x[., 1]
x[0]                // All elements of a vector
```

## Boolean Selection - Use selif(), Not Brackets

**WRONG** (Python-style):
```gauss
subset = x[x[.,1] .> 0, .];   // ERROR - can't index with boolean matrix
```

**RIGHT** (GAUSS-style):
```gauss
subset = selif(x, x[.,1] .> 0);  // Use selif() for boolean selection
```

Related functions:
| Function | Purpose |
|----------|---------|
| `selif(x, mask)` | Select rows where mask is true (non-zero) |
| `delif(x, mask)` | Delete rows where mask is true |
| `indexcat(x, val)` | Get indices where x equals val |

## Colon Range Syntax

Colon ranges work both standalone and inside brackets:

```gauss
x = 1:10;                     // Sequence 1, 2, ..., 10
x = 1:2:10;                   // Sequence 1, 3, 5, 7, 9 (start:step:end)
x = seqa(1, 1, 10);           // Same as 1:10

subset = data[1:10, .];       // Rows 1-10
subset = data[., 2:5];        // Columns 2-5
```

## Indexing Syntax

```gauss
x = rndn(5, 3);

// Basic indexing
x[1, .]           // First row, all columns
x[., 2]           // All rows, second column
x[1:3, .]         // Rows 1-3
x[., 2:3]         // Columns 2-3
x[2, 3]           // Single element (row 2, col 3)

// Index vectors
idx = { 1, 3, 5 };
x[idx, .]         // Rows 1, 3, 5

// Dataframe column selection by name
df[., "Age"]                    // Single column
df[., "Age" "Income"]           // Multiple columns (space-separated)
df[., "Age":"Zip"]              // Column range
```

## Empty Selection Pitfall

When `selif()` matches no rows, it returns a scalar missing value, not an empty matrix:

```gauss
x = { 1, 2, 3 };
result = selif(x, x .> 100);  // No matches
// result is now scalar missing (.), not empty matrix

// Check for this:
if scalmiss(result);
    print "No matches found";
endif;
```

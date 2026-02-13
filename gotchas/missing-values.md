# Missing Value Gotchas

## Creating Missing Values

```gauss
m = miss(3, 2);           // 3x2 matrix of missing values
m = miss(1, 1);           // Scalar missing value
```

Note: A period `.` by itself is NOT a missing value in code (it means "all" in indexing).

## Checking for Missing Values

**Check if ANY missing in matrix:**
```gauss
if ismiss(x);
    print "Has missing values";
endif;
```

**Create a mask of missing values:**
```gauss
// Element-wise comparison
mask = x .== miss(1, 1);  // 0/1 matrix where 1 = missing

// Or use missrv to find them
mask = x .== miss(1,1);
```

**Count missing values:**
```gauss
n_miss = sumc(sumc(x .== miss(1,1)));
```

## Removing Missing Values

```gauss
// Remove rows with ANY missing (listwise deletion)
clean = packr(x);

// Warning: packr removes entire rows. If one column has missing,
// all columns lose that row.
```

## Replacing Missing Values

```gauss
// Replace missing with a specific value
x = missrv(x, 0);              // Replace missing with 0
x = missrv(x, meanc(packr(x))); // Replace with column means

// Impute missing values
x = impute(x, "mean");         // Fill with column means
x = impute(x, "median");       // Fill with column medians
```

## Missing Value Propagation

Most operations propagate missing values:
```gauss
x = { 1, ., 3 };
y = x + 1;        // { 2, ., 4 } - missing stays missing
z = sumc(x);      // Result is missing (.) because of the missing value

// Use packr() first if you want to ignore missing:
z = sumc(packr(x));  // 4 (sum of 1 and 3)
```

## selif() Returns Missing When No Match

This is a common gotcha:

```gauss
x = { 1, 2, 3 };
result = selif(x, x .> 100);  // No rows match

// result is NOT an empty matrix - it's scalar missing (.)
// This can cause unexpected behavior downstream

// Always check:
if scalmiss(result);
    print "No matches found";
else;
    // Safe to use result
endif;
```

## Finding Indices of Missing Values

```gauss
// Get row indices where column has missing
missing_rows = indexcat(x[., 1], miss(1, 1));

// If no missing values, indexcat returns scalar missing
if scalmiss(missing_rows);
    print "No missing values";
endif;
```

## Column-wise Missing Check

```gauss
// Check which columns have any missing
has_missing = sumc(x .== miss(1,1)) .> 0;  // 1xK vector

// Get indices of columns with missing
cols_with_missing = indexcat(has_missing', 1);
```

## Dataframe Missing Values

```gauss
df = loadd("data.csv");

// Check for missing
if ismiss(df);
    print "Dataframe has missing values";
endif;

// Remove rows with missing
df_clean = packr(df);

// Impute
df_imputed = impute(df, "mean");
```

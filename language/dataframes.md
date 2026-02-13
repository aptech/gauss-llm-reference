# GAUSS Dataframes Reference

## Creating Dataframes

```gauss
// From matrix with column names
names = "Age" $| "Income" $| "Score";
df = asdf(matrix_data, names);

// From file (auto-creates dataframe)
df = loadd("mydata.csv");
df = loadd("mydata.xlsx");
df = loadd("mydata.dta");    // Stata
df = loadd("mydata.sas7bdat"); // SAS

// Create empty dataframe
df = asdf(zeros(100, 3), "A" $| "B" $| "C");
```

## Formula Strings

Formula strings are used with `loadd()`, `saved()`, and many statistical procedures to specify columns and transformations.

### Basic Selection
```gauss
// Select specific columns
data = loadd("file.csv", "Age + Income + Gender");

// Select all columns
data = loadd("file.csv", ".");

// Select all except some columns
data = loadd("file.csv", ". - ID - Timestamp");

// Column range
data = loadd("file.csv", "Age:Zip");  // All columns from Age to Zip
```

### Type Specifications
```gauss
// Categorical (factor) variable
data = loadd("file.csv", "cat(Region) + Age + Income");

// Date variable
data = loadd("file.csv", "date(OrderDate) + Amount");

// String variable (keep as string, not convert)
data = loadd("file.csv", "str(Name) + Age");

// Multiple type specs
data = loadd("file.csv", "date(Date) + cat(Region) + cat(Status) + Amount");
```

### Transformations in Formula
```gauss
// Log transform
data = loadd("file.csv", "ln(Income) + Age");

// Lag (for time series)
data = loadd("file.csv", "lag(Price, 1) + Price");

// Difference
data = loadd("file.csv", "diff(Price, 1) + Price");

// Recoding categorical
data = loadd("file.csv", "recode(Rating, 1|2|3, 'Low'|'Med'|'High')");
```

## Column Access

```gauss
// By name (single column)
ages = df[., "Age"];

// By name (multiple columns - space separated)
subset = df[., "Age" "Income" "Score"];

// By name (column range)
subset = df[., "Age":"Zip"];

// By index
col1 = df[., 1];
cols = df[., 1:3];

// Get column names
names = getColNames(df);

// Get column types
types = getColTypes(df);  // Returns: 0=numeric, 1=string, 2=date, 3=category

// Check if column exists
hasCol = contains(getColNames(df), "Age");
```

## Row Selection

```gauss
// By index
first10 = df[1:10, .];

// Boolean selection with selif
adults = selif(df, df[., "Age"] .>= 18);

// Multiple conditions
subset = selif(df, (df[., "Age"] .>= 18) .and (df[., "Income"] .> 50000));

// Select rows where category matches
region1 = selif(df, df[., "Region"] .$== "East");

// Delete rows with missing
clean = packr(df);  // Removes rows with ANY missing value
```

## Column Operations

```gauss
// Add new column with tilde operator
new_col = asdf(rndn(rows(df), 1), "NewCol");
df = df ~ new_col;

// Add column at beginning
df = new_col ~ df;

// Rename columns
df = dfname(df, "OldName", "NewName");

// Drop columns (select all except)
df = delcols(df, "DropMe");

// Reorder columns - use order() (doesn't require all column names)
df = order(df, "Col3" $| "Col1");  // Col3 first, Col1 second, rest follow

// Reorder with indexing (requires all column names)
df = df[., "Col3" "Col1" "Col2"];

// Change column type
df = setColTypes(df, "date", "OrderDate");  // Make OrderDate a date column
df = setColTypes(df, "category", "Region"); // Make Region categorical
```

## Row Operations

```gauss
// Add rows with dfappend
df = dfappend(df, new_rows_df);

// Vertical concatenation (same as dfappend)
df_combined = df1 | df2;  // Requires same columns
```

## Missing Values

```gauss
// Check for missing (returns 1 if any missing in entire matrix)
hasMissing = ismiss(df);

// Get mask of missing values (0/1 matrix same size as df)
missingMask = df .== miss();

// Remove rows with missing
df_clean = packr(df);

// Count missing in a column
n_miss = counts(df[., "Age"], miss());
// Or:
n_miss = sumc(df[., "Age"] .== miss());

// Fill missing with value
df[., "Age"] = missrv(df[., "Age"], 0);  // Replace missing with 0

// Fill missing with column mean
col = df[., "Age"];
col = missrv(col, meanc(packr(col)));
df[., "Age"] = col;

// Impute missing values
df = impute(df, "mean");    // Fill with column means
df = impute(df, "median");  // Fill with column medians
```

## Sorting

```gauss
// Sort by single column (ascending)
df_sorted = sortc(df, "Age");

// Sort by single column (descending)
df_sorted = sortc(df, "Age", -1);

// Sort by column index
df_sorted = sortc(df, 2);       // Ascending by 2nd column
df_sorted = sortc(df, 2, -1);   // Descending by 2nd column

// Get sort indices (for custom sorting)
idx = sortindc(df[., "Age"], 1);    // Ascending indices
idx = sortindc(df[., "Age"], -1);   // Descending indices
df_sorted = df[idx, .];

// Stable sort (preserves order of equal elements)
df_sorted = sortcc(df, "Category");
```

## Aggregation

```gauss
// Basic aggregation by group
result = aggregate(df, "mean", "GroupCol");

// Multiple grouping columns
result = aggregate(df, "sum", "Region" $| "Year");

// Available aggregation functions:
// "mean", "sum", "min", "max", "median", "std", "var", "count"
```

## Descriptive Statistics

```gauss
// Basic summary statistics with dstatmt
call dstatmt(df);                           // All columns
call dstatmt(df, "Age + Income");           // Specific columns

// Statistics by group - use by() in formula string
call dstatmt(df, "Sales + Units + by(Region)");

// Get statistics programmatically
struct dstatmtOut dout;
dout = dstatmt(df, "Age + Income");
print dout.mean;
print dout.std;
```

## Merging and Joining

```gauss
// Vertical concatenation (stack dataframes)
df_combined = df1 | df2;  // Requires same columns
// Or use dfappend:
df_combined = dfappend(df1, df2);

// Horizontal concatenation (add columns)
df_wide = df1 ~ df2;  // Requires same number of rows

// Merge/Join by key
df_merged = innerjoin(df1, "KeyCol", df2, "KeyCol");
df_merged = outerjoin(df1, "KeyCol", df2, "KeyCol");

// Multiple key columns
df_merged = innerjoin(df1, "Key1" $| "Key2", df2, "Key1" $| "Key2");
```

## Reshaping

```gauss
// Wide to long
df_long = dfLonger(df_wide, "Value1" $| "Value2" $| "Value3", "Measure", "Value");

// Long to wide
df_wide = dfWider(df_long, "ID", "Measure", "Value");
```

## Date Handling

GAUSS represents dates internally as POSIX timestamps (seconds since 1970-01-01).

```gauss
// Load with date column
df = loadd("file.csv", "date(OrderDate) + Amount");

// Create date from components
dt = timeutc(2024, 6, 15, 0, 0, 0);  // Returns POSIX timestamp

// Format date for display using posixToStrc
date_str = posixToStrc(dt, "%Y-%m-%d");           // "2024-06-15"
date_str = posixToStrc(dt, "%B %d, %Y");          // "June 15, 2024"
date_str = posixToStrc(dt, "%Y-%m-%d %H:%M:%S");  // With time

// Parse date string to POSIX using strcToPosix
dt = strcToPosix("2024-06-15", "%Y-%m-%d");
dt = strcToPosix("June 15, 2024", "%B %d, %Y");

// Common format codes:
// %Y = 4-digit year, %y = 2-digit year
// %m = month (01-12), %B = month name, %b = abbreviated month
// %d = day (01-31)
// %H = hour (00-23), %M = minute, %S = second
// %j = day of year (001-366)

// Extract date components
yr = year(df[., "Date"]);
mo = month(df[., "Date"]);
dy = dayofmonth(df[., "Date"]);
dow = dayofweek(df[., "Date"]);  // 1=Sunday, 7=Saturday

// Date arithmetic (POSIX is in seconds)
tomorrow = today + 86400;           // Add one day (86400 seconds)
next_week = today + 7*86400;        // Add one week
hours_diff = (date2 - date1)/3600;  // Difference in hours
```

## Category Operations

```gauss
// Get category labels
labels = getColLabels(df, "Region");

// Get category key values
keys = getcollabelskeys(df, "Region");

// Recode categories
df = reclassify(df, "Region", "East"|"West", "Atlantic"|"Pacific");

// Create category from numeric
df = setColTypes(df, "category", "Rating");
```

## Common Patterns

### Data Cleaning Pipeline
```gauss
// Load and clean data
df = loadd("raw_data.csv");

// Check dimensions
print "Rows:" rows(df) "Cols:" cols(df);

// Preview
head(df);

// Check for missing (ismiss returns 1 if any missing)
print ("Missing values:" ismiss(df));

// Remove rows with missing
df = packr(df);

// Filter outliers (keep within 3 std dev)
for i (1, cols(df), 1);
    col = df[., i];
    mu = meanc(col);
    sigma = stdc(col);
    mask = (col .> mu - 3*sigma) .and (col .< mu + 3*sigma);
    df = selif(df, mask);
endfor;
```

### Group-wise Operations
```gauss
// Calculate group statistics
groups = unique(df[., "Region"]);

for i (1, rows(groups), 1);
    group_data = selif(df, df[., "Region"] .$== groups[i]);
    print groups[i] "mean:" meanc(group_data[., "Sales"]);
endfor;

// Or use aggregate
group_stats = aggregate(df, "mean", "Region");
```

### Time Series Preparation
```gauss
// Load with date
df = loadd("prices.csv", "date(Date) + Price + Volume");

// Sort by date
df = sortc(df, "Date");

// Create lagged variables
lag1 = asdf(lagn(df[., "Price"], 1), "Price_L1");
lag2 = asdf(lagn(df[., "Price"], 2), "Price_L2");
df = df ~ lag1 ~ lag2;

// Create returns
price = df[., "Price"];
returns = (price - lagn(price, 1)) ./ lagn(price, 1);
returns_df = asdf(returns, "Returns");
df = df ~ returns_df;

// Remove first rows with missing lags
df = packr(df);
```

## Saving Data

```gauss
// CSV
saved(df, "output.csv");

// Excel
saved(df, "output.xlsx");

// GAUSS dataset (preserves all metadata)
saved(df, "output.gdat");

// Save specific columns
saved(df[., "Age" "Income"], "subset.csv");
```

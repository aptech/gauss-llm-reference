# GAUSS Panel Data Reference

Panel data has observations across both time and cross-sectional units (e.g., multiple firms over multiple years).

## Panel Data Structure

Panel data typically has:
- **ID column**: Identifies the cross-sectional unit (firm, country, individual)
- **Time column**: Identifies the time period
- **Variables**: Measured values

```gauss
// Example panel structure:
// ID    Year    GDP    Population
// USA   2020    21.0   331
// USA   2021    23.0   332
// CAN   2020    1.6    38
// CAN   2021    1.9    38
```

## Loading Panel Data

```gauss
// Load panel data
df = loadd("panel.csv", "cat(ID) + date(Year) + GDP + Population");

// Ensure proper sorting (by ID, then Time)
df = sortc(df, "ID");           // Sort by ID first
df = sortmc(df, "ID" $| "Year"); // Sort by both
```

## Checking Panel Balance

```gauss
// Check if panel is balanced (all units have same time periods)
balanced = pdIsBalanced(df);

// Get panel summary
pdSummary(df);                  // Prints summary info
```

## Panel Transformations

### Within-Group Operations (pdBalance)

```gauss
// Balance an unbalanced panel (fill missing periods)
df_balanced = pdBalance(df);
```

### Lagging by Group
```gauss
// Create lag within each panel unit
df_lagged = pdLag(df, 1);       // Lag 1 period within group
df_lagged = pdLag(df, 4);       // Lag 4 periods

// Multiple lags
for k (1, 4, 1);
    lag_k = pdLag(df[., "GDP"], k);
    df = df ~ asdf(lag_k, "GDP_L" $+ ntos(k));
endfor;
```

### First Differences by Group
```gauss
// First difference within each panel unit
df_diff = pdDiff(df, 1);

// Higher-order differences
df_diff2 = pdDiff(df, 2);
```

### Growth Rates by Group
```gauss
// Compute growth rates
gdp = df[., "GDP"];
gdp_lag = pdLag(df, 1)[., "GDP"];
growth = (gdp - gdp_lag) ./ gdp_lag;
df = df ~ asdf(growth, "GDP_Growth");
```

## Reshaping Panel Data

### Wide to Long (dfLonger)
```gauss
// Convert wide format to long format
// Wide: ID, Year, Var1, Var2, Var3
// Long: ID, Year, Variable, Value

df_wide = loadd("wide_data.csv");

// Get variable columns (exclude ID and Year)
columns = "Var1" $| "Var2" $| "Var3";
names_to = "Variable";
values_to = "Value";

df_long = dfLonger(df_wide, columns, names_to, values_to);

// With control structure for prefix removal
struct pivotControl pctl;
pctl = pivotControlCreate();
pctl.names_prefix = "Var";     // Remove "Var" prefix

df_long = dfLonger(df_wide, columns, names_to, values_to, pctl);
```

### Long to Wide (dfWider)
```gauss
// Convert long format to wide format
df_wide = dfWider(df_long, "ID", "Variable", "Value");
```

## Group-wise Operations

### Aggregate by Group
```gauss
// Mean by group
group_means = aggregate(df, "mean", "ID");

// Multiple group columns
yearly_means = aggregate(df, "mean", "ID" $| "Year");

// Sum, count, etc.
group_sums = aggregate(df, "sum", "ID");
group_counts = aggregate(df, "count", "ID");
```

### Within-Group Statistics
```gauss
// Demean within groups (for fixed effects)
ids = unique(df[., "ID"]);
n = rows(df);
x_demeaned = zeros(n, 1);

for i (1, rows(ids), 1);
    mask = df[., "ID"] .$== ids[i];
    group_data = selif(df[., "GDP"], mask);
    group_mean = meanc(group_data);
    idx = indexcat(mask, 1);
    x_demeaned[idx] = group_data - group_mean;
endfor;
```

### Lead by Group
```gauss
// Lead (forward) values
df_lead = pdLag(df, -1);        // Negative lag = lead
```

## Panel Regression

### Pooled OLS
```gauss
// Simple pooled regression (ignores panel structure)
struct olsmtOut out;
out = olsmt(df, "Y ~ X1 + X2 + X3");
```

### Fixed Effects (Within Transformation)
```gauss
// Manual fixed effects via demeaning
// Step 1: Demean all variables within groups
ids = unique(df[., "ID"]);
vars = "Y" $| "X1" $| "X2";

df_demeaned = df;
for v (1, rows(vars), 1);
    varname = vars[v];
    demeaned = zeros(rows(df), 1);

    for i (1, rows(ids), 1);
        mask = df[., "ID"] .$== ids[i];
        group_data = selif(df[., varname], mask);
        group_mean = meanc(group_data);
        idx = indexcat(mask, 1);
        demeaned[idx] = group_data - group_mean;
    endfor;

    df_demeaned[., varname] = demeaned;
endfor;

// Step 2: Run OLS on demeaned data
struct olsmtOut out;
out = olsmt(df_demeaned, "Y ~ X1 + X2");
```

### LSDV (Least Squares Dummy Variables)
```gauss
// Include dummy variables for each unit (minus one for reference)
// Create dummies for ID
ids = unique(df[., "ID"]);
n_ids = rows(ids);

for i (2, n_ids, 1);            // Start from 2 (first is reference)
    dummy = df[., "ID"] .$== ids[i];
    df = df ~ asdf(dummy, "D_" $+ ntos(ids[i]));
endfor;

// Include dummies in regression
out = olsmt(df, "Y ~ X1 + X2 + D_2 + D_3 + ...");
```

## Common Panel Data Patterns

### Creating Panel from Cross-Section Files
```gauss
// Load multiple years of cross-sectional data
years = seqa(2015, 1, 10);      // 2015-2024
combined = {};

for i (1, rows(years), 1);
    yr = years[i];
    filename = sprintf("data_%d.csv", yr);
    df_yr = loadd(filename);

    // Add year column
    year_col = asdf(ones(rows(df_yr), 1) * yr, "Year");
    df_yr = df_yr ~ year_col;

    combined = combined | df_yr;
endfor;

saved(combined, "panel_data.csv");
```

### Identifying First/Last Observation per Group
```gauss
// Sort by ID and Time
df = sortmc(df, "ID" $| "Year");

// Get indices of first observation per group
ids = unique(df[., "ID"]);
first_obs = zeros(rows(ids), 1);
last_obs = zeros(rows(ids), 1);

for i (1, rows(ids), 1);
    mask = df[., "ID"] .$== ids[i];
    idx = indexcat(mask, 1);
    first_obs[i] = minc(idx);
    last_obs[i] = maxc(idx);
endfor;
```

### Computing Time-Varying Averages
```gauss
// Average of all other units in same time period
years = unique(df[., "Year"]);
leave_out_mean = zeros(rows(df), 1);

for t (1, rows(years), 1);
    yr = years[t];
    year_mask = df[., "Year"] .== yr;
    year_data = selif(df, year_mask);

    ids_in_year = unique(year_data[., "ID"]);

    for i (1, rows(ids_in_year), 1);
        id = ids_in_year[i];
        // Mean of all units except this one
        other_mask = year_data[., "ID"] .$!= id;
        other_data = selif(year_data[., "GDP"], other_mask);
        leave_out = meanc(other_data);

        // Find position in original df
        df_mask = (df[., "Year"] .== yr) .and (df[., "ID"] .$== id);
        idx = indexcat(df_mask, 1);
        leave_out_mean[idx] = leave_out;
    endfor;
endfor;
```

### Handling Unbalanced Panels
```gauss
// Fill gaps with missing values
df_balanced = pdBalance(df);

// Or: keep only complete cases
ids = unique(df[., "ID"]);
years = unique(df[., "Year"]);
complete_ids = {};

for i (1, rows(ids), 1);
    id = ids[i];
    id_data = selif(df, df[., "ID"] .$== id);
    if rows(id_data) == rows(years);
        complete_ids = complete_ids | id;
    endif;
endfor;

// Keep only complete IDs
mask = rowcontains(df[., "ID"], complete_ids);
df_balanced = selif(df, mask);
```

## Panel Summary Statistics

```gauss
// Overall statistics
call dstatmt(df, "GDP + Population");

// By group statistics
call dstatmt(df, "GDP + Population + by(ID)");

// Number of observations per unit
obs_per_unit = aggregate(df, "count", "ID");

// Number of time periods per unit
periods_per_unit = zeros(rows(ids), 1);
for i (1, rows(ids), 1);
    mask = df[., "ID"] .$== ids[i];
    periods_per_unit[i] = sumc(mask);
endfor;
```

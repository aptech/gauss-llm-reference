# GAUSS I/O Reference

## Loading Data

### Universal Data Loading (loadd)
`loadd` is the primary function for loading data. It auto-detects format.

```gauss
// Load entire file
data = loadd("mydata.csv");
data = loadd("mydata.xlsx");
data = loadd("mydata.dta");        // Stata
data = loadd("mydata.sas7bdat");   // SAS
data = loadd("mydata.gdat");       // GAUSS native

// Load specific columns using formula string
data = loadd("file.csv", "Age + Income + Gender");

// Load all except some columns
data = loadd("file.csv", ". - ID - Timestamp");

// Load with type specifications
data = loadd("file.csv", "date(Date) + cat(Region) + Sales");

// Load column range
data = loadd("file.csv", "Age:Zip");
```

### Excel Files
```gauss
// Basic load (first sheet)
data = loadd("file.xlsx");

// Specific sheet
data = xlsReadM("file.xlsx", "A1:Z100", 2);  // Sheet 2, range A1:Z100

// With headers
data = xlsReadSA("file.xlsx", "A1:Z1", 1);   // Read strings (headers)

// Load as dataframe with types
data = loadd("file.xlsx", "date(Date) + cat(Category) + Value");
```

### CSV Files
```gauss
// Standard load
data = loadd("file.csv");

// Custom delimiter (tab)
data = loadd("file.txt", ".", ",", 0);  // Last arg: 0=comma, 1=tab, etc.

// With specific encoding
fh = fopen("file.csv", "r,UTF-8");
// ... read operations
fh = fclose(fh);
```

### GAUSS Native Formats
```gauss
// Matrix file (.fmt)
data = loadm("matrix.fmt");

// Dataset file (.dat) - legacy format
open fp = "olddata.dat" for read;
data = readr(fp, 100);  // Read 100 rows
fp = close(fp);

// GAUSS data archive (.gda)
data = gdaReadSome("archive.gda", "varname");
```

## Saving Data

### Universal Save (saved)
```gauss
// Save to various formats
saved(data, "output.csv");
saved(data, "output.xlsx");
saved(data, "output.gdat");        // GAUSS native (preserves metadata)
saved(data, "output.dta");         // Stata format

// Save specific columns
saved(data[., "Col1" "Col2"], "subset.csv");
```

### Excel Export
```gauss
// Write matrix
xlsWrite(data, "file.xlsx", "A1", 1);  // Start at A1, sheet 1

// Write string array
xlsWrite(headers, "file.xlsx", "A1", 1);
xlsWrite(data, "file.xlsx", "A2", 1);

// Append to existing sheet
xlsWrite(new_data, "file.xlsx", "A100", 1);
```

### Matrix Files
```gauss
// Save matrix
savem(x, "matrix.fmt");

// Load matrix
x = loadm("matrix.fmt");
```

## Low-Level File I/O

### Text Files
```gauss
// Open file
fh = fopen("file.txt", "r");    // Read mode
fh = fopen("file.txt", "w");    // Write mode (overwrite)
fh = fopen("file.txt", "a");    // Append mode

// Read entire file as string
content = fgets(fh, -1);        // -1 = read all

// Read line by line
do while not feof(fh);
    line = fgets(fh);
    // process line
endo;

// Write to file
fputs(fh, "Hello World\n");

// Close file
fh = fclose(fh);
```

### Binary Files
```gauss
// Open binary file
fh = fopen("data.bin", "rb");   // Read binary
fh = fopen("data.bin", "wb");   // Write binary

// Read/write raw bytes
bytes = fread(fh, 100);         // Read 100 bytes
fwrite(fh, data);               // Write data

fh = fclose(fh);
```

### Checking File Existence
```gauss
if fileExist("myfile.csv");
    data = loadd("myfile.csv");
else;
    print "File not found";
endif;
```

## Working with Paths

```gauss
// Get file parts
dir = pathDir("C:/data/file.csv");       // "C:/data"
name = pathName("C:/data/file.csv");     // "file"
ext = pathExt("C:/data/file.csv");       // ".csv"

// Combine paths
fullpath = pathcat("C:/data", "file.csv");

// Current directory
cwd = getcwd();

// Change directory
chdir("C:/newpath");

// List files
files = filesa("*.csv");         // All CSV files in current dir
files = filesa("data/*.xlsx");   // Excel files in data folder
```

## Database Connectivity

### ODBC (Database Connection)
```gauss
// Connect to database
db = dbOpen("ODBC;DSN=mydb;UID=user;PWD=pass");

// Execute query
result = dbExecQuery(db, "SELECT * FROM customers WHERE region='East'");

// Read results
data = dbFetch(result, -1);      // -1 = fetch all rows

// Close connection
dbClose(db);
```

### SQL Examples
```gauss
// Parameterized query
query = "SELECT * FROM sales WHERE date > ?";
result = dbExecQuery(db, query, "2024-01-01");

// Insert data
dbExecQuery(db, "INSERT INTO table VALUES (?, ?, ?)", val1, val2, val3);

// Get table info
cols = dbColumns(db, "tablename");
```

## Web Data

### HTTP Requests
```gauss
// GET request
response = httpGet("https://api.example.com/data");

// POST request
response = httpPost("https://api.example.com/submit", postdata);

// With headers
headers = "Content-Type: application/json";
response = httpPost("https://api.example.com/api", jsondata, headers);
```

### JSON
```gauss
// Parse JSON string
data = jsonParse(json_string);

// Access JSON fields (depends on structure)
// JSON arrays become matrices
// JSON objects become structures

// Create JSON from matrix
json_str = jsonWrite(data);
```

## Data Streaming (Large Files)

### Reading Large Files in Chunks
```gauss
// Get file info
{ nrows, ncols, vnames, vtypes } = dstatmt("largefile.gdat", 0);

// Read in chunks
chunksize = 10000;
nchunks = ceil(nrows / chunksize);

for i (1, nchunks, 1);
    startrow = (i-1)*chunksize + 1;
    endrow = minc(i*chunksize | nrows);

    chunk = loadd("largefile.gdat", ".", startrow, endrow);
    // Process chunk
endfor;
```

### Memory-Mapped Files
```gauss
// For very large matrices that don't fit in memory
// Use GAUSS data files (.gdat) which support random access
```

## Common Patterns

### Load, Process, Save Pipeline
```gauss
// Load
data = loadd("raw_data.csv");

// Clean
data = packr(data);              // Remove missing
data = selif(data, data[., "Amount"] .> 0);  // Filter

// Transform
data = data ~ asdf(ln(data[., "Amount"]), "LogAmount");

// Save
saved(data, "processed_data.csv");
```

### Merge Multiple Files
```gauss
// Get list of files
files = filesa("data/*.csv");
n = rows(files);

// Load and combine
combined = loadd("data/" $+ files[1]);

for i (2, n, 1);
    newdata = loadd("data/" $+ files[i]);
    combined = combined | newdata;  // Vertical concat
endfor;

saved(combined, "combined.csv");
```

### Export Results Table
```gauss
// Create results
coefs = { 1.5, 2.3, -0.8 };
se = { 0.3, 0.5, 0.2 };
pval = { 0.001, 0.01, 0.05 };
varnames = "Intercept" $| "X1" $| "X2";

// Combine into table
results = asdf(coefs ~ se ~ pval, "Coefficient" $| "Std Error" $| "P-Value");

// Add row names
results = varnames ~ results;

// Save
saved(results, "regression_results.csv");
```

### Configuration Files
```gauss
// Simple key-value config file
fh = fopen("config.txt", "r");
do while not feof(fh);
    line = strtrim(fgets(fh));
    if strlen(line) > 0 and strindx(line, "#") != 1;
        parts = strsplit(line, "=");
        key = strtrim(parts[1]);
        value = strtrim(parts[2]);
        // Store key-value pair
    endif;
endo;
fh = fclose(fh);
```

## File Format Reference

| Extension | Description | Load Function |
|-----------|-------------|---------------|
| `.csv` | Comma-separated | `loadd` |
| `.xlsx` | Excel | `loadd`, `xlsReadM` |
| `.xls` | Excel (old) | `loadd`, `xlsReadM` |
| `.dta` | Stata | `loadd` |
| `.sas7bdat` | SAS | `loadd` |
| `.gdat` | GAUSS dataset | `loadd` |
| `.fmt` | GAUSS matrix | `loadm` |
| `.h5`, `.hdf5` | HDF5 | `loadd` |
| `.json` | JSON | `jsonParse` (from string) |

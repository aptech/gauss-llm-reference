# GAUSS Strings Reference

## String Basics

```gauss
// String literal
s = "Hello, World!";

// String combine (merges into one string)
s = "Hello" $+ " " $+ "World";  // "Hello World" (single string)

// String horizontal concatenation (creates columns)
s = "Hello" $~ "World";          // 1x2 array: s[1,1]="Hello", s[1,2]="World"

// String vertical concatenation (creates rows)
sa = "apple" $| "banana" $| "cherry";  // 3x1 string array

// Building a 2x2 string array
sa = ("a" $~ "b") $| ("c" $~ "d");  // 2x2: row1="a","b"; row2="c","d"
```

## String Concatenation Summary

| Operator | Name | Result |
|----------|------|--------|
| `$+` | Combine | Merges strings into one: `"a" $+ "b"` → `"ab"` |
| `$~` | Horizontal concat | Creates columns: `"a" $~ "b"` → 1x2 array |
| `$\|` | Vertical concat | Creates rows: `"a" $\| "b"` → 2x1 array |

## String Comparison

```gauss
// Element-wise string equality (returns 0/1 matrix)
result = sa .$== "apple";     // 1 where equal, 0 otherwise
result = sa .$!= "apple";     // 1 where not equal

// String comparison
result = strcmp(s1, s2);      // 0 if equal, <0 if s1<s2, >0 if s1>s2

// Case-insensitive comparison
result = strcmpi(s1, s2);     // Same as strcmp but case-insensitive
```

## String Manipulation

### Trimming
```gauss
s = "  hello  ";
s = strtriml(s);    // "hello  " - trim left
s = strtrimr(s);    // "  hello" - trim right
s = strtrim(s);     // "hello"   - trim both sides
```

### Case Conversion
```gauss
s = "Hello World";
s = lower(s);       // "hello world"
s = upper(s);       // "HELLO WORLD"
```

### Substring Operations
```gauss
s = "Hello World";

// Extract substring
sub = substr(s, 1, 5);       // "Hello" (start=1, length=5)
sub = substr(s, 7, 5);       // "World"

// Find position of substring
pos = strindx(s, "World");   // 7 (1-indexed position)
pos = strindx(s, "xyz");     // 0 (not found)

// Find from right
pos = strrindx(s, "o");      // 8 (position of last 'o')
```

### String Length
```gauss
s = "Hello";
len = strlen(s);             // 5

// For string arrays, returns matrix of lengths
sa = "apple" $| "hi";
lens = strlen(sa);           // 5, 2
```

### Replace and Remove
```gauss
s = "Hello World";

// Replace all occurrences
s = strreplace(s, "World", "GAUSS");  // "Hello GAUSS"

// Remove characters
s = strreplace(s, " ", "");           // "HelloWorld"
```

## String Splitting and Joining

### Splitting
```gauss
s = "apple,banana,cherry";

// Split by delimiter
parts = strsplit(s, ",");    // 3x1 string array

// Split with multiple delimiters
s = "apple;banana,cherry";
parts = strsplit(s, ",;");   // Split on , or ;

// Split on whitespace
s = "one two  three";
parts = strsplit(s, " ");    // Note: may have empty strings
```

### Joining
```gauss
sa = "apple" $| "banana" $| "cherry";

// Join with delimiter
s = strjoin(sa, ", ");       // "apple, banana, cherry"
s = strjoin(sa, "-");        // "apple-banana-cherry"

// strcombine (adds delimiter after each, including last)
s = strcombine(sa, ",", 0);  // "apple,banana,cherry,"
```

## Formatting and Conversion

### Number to String
```gauss
x = 3.14159;

// Basic conversion
s = ntos(x);                 // "3.14159"
s = ntos(x, 2);              // "3.14" (2 decimal places)

// sprintf for formatted output
s = sprintf("%0.2f", x);     // "3.14"
s = sprintf("%10.4f", x);    // "    3.1416" (width 10, 4 decimals)
s = sprintf("%d", 42);       // "42" (integer)
s = sprintf("Value: %g", x); // "Value: 3.14159"

// Scientific notation
s = sprintf("%e", 1234.5);   // "1.234500e+03"
s = sprintf("%.2e", 1234.5); // "1.23e+03"
```

### String to Number
```gauss
s = "3.14";
x = stof(s);                 // 3.14 (string to float)

// String array to numeric matrix
sa = "1" $| "2" $| "3";
x = stof(sa);                // 3x1 matrix: 1, 2, 3
```

### Matrix to String Array
```gauss
x = { 1.5, 2.7, 3.9 };
sa = ntos(x);                // 3x1 string array

// With formatting
sa = ntos(x, 2);             // "1.50", "2.70", "3.90"
```

## String Search and Pattern Matching

### Simple Search
```gauss
s = "Hello World";

// Check if contains substring
found = strindx(s, "World") > 0;  // 1 (true)

// Count occurrences
count = strcnt(s, "o");           // 2
```

### Regular Expressions
```gauss
s = "Price: $123.45";

// Match pattern
match = strregexp(s, "\\$[0-9.]+");  // "$123.45"

// Check if matches
matches = strregexp(s, "^Price:");   // "Price:"

// Replace with regex
s = strregexpreplace(s, "[0-9]+", "XXX");  // "Price: $XXX.XXX"

// Extract groups
s = "John Smith, age 30";
parts = strregexp(s, "(\\w+) (\\w+), age (\\d+)", 1);  // Groups
```

## String Arrays

### Creating String Arrays
```gauss
// Vertical concatenation (rows)
names = "Alice" $| "Bob" $| "Charlie";  // 3x1

// Horizontal concatenation (columns)
row = "Alice" $~ "Bob" $~ "Charlie";    // 1x3

// Combine both
grid = ("a" $~ "b") $| ("c" $~ "d");    // 2x2

// From loaded data
names = getColNames(df);

// Reshape string array
sa = "a" $| "b" $| "c" $| "d";
sa2 = reshape(sa, 2, 2);     // 2x2 string array
```

### String Array Operations
```gauss
names = "Alice" $| "Bob" $| "Charlie";

// Select elements
first = names[1];            // "Alice"
subset = names[1:2];         // "Alice", "Bob"

// Unique strings
unique_names = unique(names);

// Sort string array
sorted = sortc(names, 1);    // Alphabetical sort
```

## Common Patterns

### Building File Paths
```gauss
dir = "/home/user/data";
filename = "results.csv";
path = dir $+ "/" $+ filename;  // "/home/user/data/results.csv"
```

### Parsing Delimited Data
```gauss
line = "John,Smith,30,Engineer";
parts = strsplit(line, ",");
fname = parts[1];    // "John"
lname = parts[2];    // "Smith"
age = stof(parts[3]); // 30
job = parts[4];      // "Engineer"
```

### Creating Variable Names
```gauss
// Generate numbered names
prefix = "var";
n = 5;
names = "";
for i (1, n, 1);
    names = names $| (prefix $+ ntos(i));
endfor;
// names: "var1", "var2", "var3", "var4", "var5"

// Using sprintf for padding
names = "";
for i (1, n, 1);
    names = names $| sprintf("%s%02d", prefix, i);
endfor;
// names: "var01", "var02", etc.
```

### Extracting File Extension
```gauss
filename = "data.csv";
pos = strrindx(filename, ".");
if pos > 0;
    ext = substr(filename, pos+1, strlen(filename)-pos);
    name = substr(filename, 1, pos-1);
endif;
// ext = "csv", name = "data"
```

### HTML/XML Escaping
```gauss
s = "Tom & Jerry <show>";
s = strreplace(s, "&", "&amp;");
s = strreplace(s, "<", "&lt;");
s = strreplace(s, ">", "&gt;");
```

## Print Formatting

```gauss
// Basic print (space-separated list)
x = 5;
y = 10;
print "x =" x "y =" y;    // x = 5 y = 10

// For expressions, use parentheses
print "sum =" (x+y);       // sum = 15

// Format matrix output
format /rd 8,2;           // Right-justified, 8 wide, 2 decimals
print matrix_data;

// Reset format
format /rd 1,0;           // Reset to defaults

// sprintf for custom formatting
msg = sprintf("The value is %.2f", 3.14159);
print msg;
```

## Character Functions

```gauss
// Character to ASCII code
code = ord("A");         // 65

// ASCII code to character
ch = chr(65);            // "A"

// Check character type
isalpha = ord(ch) >= 65 and ord(ch) <= 90;  // Is uppercase letter
```

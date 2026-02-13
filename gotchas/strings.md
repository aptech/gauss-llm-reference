# String Gotchas

## Concatenation - Use $+ Not +

**WRONG**:
```gauss
s = "hello" + "world";   // ERROR - + doesn't work on strings
```

**RIGHT**:
```gauss
s = "hello" $+ "world";  // "helloworld"
```

## String Array Operators

| Operator | Result | Use For |
|----------|--------|---------|
| `$+` | Single string | Combining text into one string |
| `$\|` | Column vector | Column names, vertical lists |
| `$~` | Row vector | Horizontal string arrays |

**Building column names** (need column vector):
```gauss
names = "Age" $| "Income" $| "Score";  // 3x1 string array
df = asdf(data, names);                 // Correct
```

**WRONG**:
```gauss
names = "Age" $+ "Income" $+ "Score";  // "AgeIncomeScore" (single string!)
```

## String Comparison

| Operator | Type | Use |
|----------|------|-----|
| `$==` | Matrix-wide | Check if all strings equal |
| `.$==` | Element-wise | Create mask for filtering |

```gauss
// Filter dataframe by string column
region_east = selif(df, df[., "Region"] .$== "East");

// NOT this (returns scalar):
region_east = selif(df, df[., "Region"] $== "East");  // Wrong!
```

## String Functions Quick Reference

```gauss
// Length
strlen("hello")           // 5

// Substrings
strsect("hello", 1, 3)    // "hel" (start, length)

// Find
strindx("hello", "ll")    // 3 (position of "ll")

// Replace
strreplace("hello", "ll", "r")  // "hero"

// Case
upper("hello")            // "HELLO"
lower("HELLO")            // "hello"

// Trim whitespace
strtrim("  hello  ")      // "hello"
strtriml("  hello  ")     // "hello  " (left only)
strtrimr("  hello  ")     // "  hello" (right only)

// Split/join
strsplit("a,b,c", ",")    // 3x1 string array
strjoin(names, ",")       // "Age,Income,Score"
```

## Number to String Conversion

**Use `ntos()` for simple conversion** (preferred):
```gauss
s = ntos(3.14159);        // "3.14159" (default 6 digits)
s = ntos(6.725301, 3);    // "6.73" (3 significant digits)
s = ntos(pi, 10);         // "3.141592654"
```

**Use `sprintf()` for formatted strings with multiple values**:
```gauss
s = sprintf("Name: %s, Value: %g", "test", 3.14);
s = sprintf("Count: %d, Ratio: %.2f", 42, 0.756);
s = sprintf("%10.4f", 123.456);  // "  123.4560"
```

**Use `ftos()` for single-value formatted output**:
```gauss
// ftos(value, format, field_width, precision)
s = ftos(929.857, "%*.*lf", 7, 2);     // "929.86"
s = ftos(929.857, "%*.*lE", 1, 4);     // "9.2986E+002"

// With embedded text
s = ftos(3.5, "Time: %*.*lf seconds.", 1, 1);  // "Time: 3.5 seconds."
```

## Print Statement with Strings

```gauss
// Space-separated items (correct)
print "Result:" x;

// NOT comma-separated
print "Result:", x;       // ERROR - no commas in print

// String continuation
print "Part 1";;          // ;; suppresses newline
print " Part 2";          // Continues on same line
```

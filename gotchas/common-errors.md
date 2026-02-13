# Common Errors

## Missing Semicolons

Every statement in GAUSS must end with a semicolon.

**WRONG**:
```gauss
x = 5
y = x + 1
```

**RIGHT**:
```gauss
x = 5;
y = x + 1;
```

## Curly Braces Don't Work Inline

Matrix literals with `{ }` cannot be used directly as function arguments.

**WRONG**:
```gauss
y = sumc({1,2,3});        // ERROR - braces don't work inline
y = meanc({1, 2, 3, 4});  // ERROR
```

**RIGHT**:
```gauss
y = sumc(1|2|3);          // Use | for vertical concat
y = sumr(1~2~3);          // Use ~ for horizontal concat

// Or assign first, then use
x = { 1, 2, 3 };
y = sumc(x);
```

## Colon Range Outside Brackets

The colon range syntax only works inside index brackets.

**WRONG**:
```gauss
x = 1:10;                 // ERROR - not valid GAUSS
```

**RIGHT**:
```gauss
x = seqa(1, 1, 10);       // Creates 1, 2, 3, ..., 10

// Colon works inside brackets:
subset = data[1:10, .];   // First 10 rows
subset = data[., 2:5];    // Columns 2 through 5
```

## Using = Instead of == in Conditions

**WRONG**:
```gauss
if x = 5;                 // This ASSIGNS 5 to x!
    print "equal";
endif;
```

**RIGHT**:
```gauss
if x == 5;                // This COMPARES x to 5
    print "equal";
endif;
```

## Forgetting the Dot in Element-wise Operations

**WRONG**:
```gauss
c = a * b;                // Matrix multiply (probably not what you want)
mask = x > 0;             // Scalar result (1 if ALL > 0)
```

**RIGHT**:
```gauss
c = a .* b;               // Element-wise multiply
mask = x .> 0;            // Element-wise comparison (0/1 matrix)
```

## Print Statement Commas

**WRONG**:
```gauss
print "Value:", x;        // ERROR - no commas
print("x =", x);          // ERROR - print is not a function
```

**RIGHT**:
```gauss
print "Value:" x;         // Space-separated, no commas
print "x =" x "y =" y;    // Multiple items, spaces only
```

## Boolean Indexing Instead of selif()

**WRONG** (Python-style):
```gauss
subset = x[x .> 0];       // ERROR - can't use boolean as index
subset = data[mask, .];   // ERROR
```

**RIGHT** (GAUSS-style):
```gauss
subset = selif(x, x .> 0);       // Use selif() for boolean selection
subset = selif(data, mask);
```

## Empty Results from selif()

When no rows match, `selif()` returns scalar missing, not an empty matrix.

```gauss
result = selif(x, x .> 1000);  // If no matches...
// result is scalar missing (.), not empty matrix

// Check for this:
if scalmiss(result);
    print "No matches";
endif;
```

## Wrong String Operator

**WRONG**:
```gauss
s = "a" + "b";            // ERROR - use $+ for strings
names = "A" + "B" + "C";  // ERROR
```

**RIGHT**:
```gauss
s = "a" $+ "b";           // "ab"
names = "A" $| "B" $| "C"; // 3x1 string array (for column names)
```

## Procedure Return Without retp()

**WRONG**:
```gauss
proc (1) = double(x);
    return x * 2;         // ERROR - use retp(), not return
endp;
```

**RIGHT**:
```gauss
proc (1) = double(x);
    retp(x * 2);          // Correct
endp;
```

## Missing endp/endif/endfor

Every control structure needs its closing statement:

```gauss
// Procedure
proc (1) = myFunc(x);
    ...
endp;                     // Required

// If statement
if condition;
    ...
endif;                    // Required

// For loop
for i (1, 10, 1);
    ...
endfor;                   // Required

// Do while
do while condition;
    ...
endo;                     // Required (note: endo, not enddo)
```

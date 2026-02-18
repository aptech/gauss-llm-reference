# Variable Scope Gotchas

## `local` Only Inside Procedures

**WRONG** - `local` at global scope:
```gauss
local x;              // ERROR: "LOCAL outside of procedure"
x = { 1, 2, 3 };
```

**RIGHT** - just assign at global scope:
```gauss
x = { 1, 2, 3 };      // Correct - no declaration needed in main code
```

**RIGHT** - `local` inside procedures:
```gauss
proc (1) = myProc(x);
    local a, b, result;   // Correct - inside proc
    a = x + 1;
    b = x * 2;
    result = a + b;
    retp(result);
endp;
```

## Declare All Locals at Top of Procedure

`local` variables are scoped to the entire procedure, not to blocks. Declare once at the top.

**WRONG** - declaring same variable twice:
```gauss
proc (1) = badExample(x);
    local i;
    for i (1, 10, 1);
        local temp;       // First declaration
        temp = x[i];
    endfor;

    local temp;           // ERROR - temp already declared above!
    retp(x);
endp;
```

**RIGHT** - declare all at top:
```gauss
proc (1) = goodExample(x);
    local i, temp, result;    // All locals declared once at top

    for i (1, 10, 1);
        temp = x[i];
    endfor;

    result = temp * 2;
    retp(result);
endp;
```

## Procedure Parameters Don't Need `local`

**WRONG**:
```gauss
proc (1) = myProc(x);
    local x;              // ERROR - x is already a parameter
    retp(x + 1);
endp;
```

**RIGHT**:
```gauss
proc (1) = myProc(x);
    retp(x + 1);          // x is already available as parameter
endp;
```

## Global Variables

Variables assigned outside procedures are global and accessible everywhere:

```gauss
// Global scope
data = loadd("myfile.csv");
threshold = 0.05;

proc (1) = analyze(x);
    local result;
    // Can access global 'threshold' here
    result = selif(x, x .> threshold);
    retp(result);
endp;
```

Note: Variables assigned inside a procedure without `local` declaration will also be global - this is usually a mistake. Always declare locals explicitly.

## Function Pointers

Function pointers only work with GAUSS procedures, NOT built-in C functions:

```gauss
fn = &ols;            // OK - ols is a GAUSS proc
fn = &myCustomProc;   // OK - user-defined proc
fn = &sumc;           // ERROR - sumc is a built-in C function
fn = &meanc;          // ERROR - meanc is a built-in C function
```

When using function pointers, the assignment MUST come before the type declaration:

**WRONG**:
```gauss
proc (1) = myProc(x);
    local fn:proc;        // Declaration first - WRONG
    fn = &ols;
    retp(fn(x));
endp;
```

**RIGHT**:
```gauss
proc (1) = myProc(x);
    local fn;
    fn = &ols;            // Assignment first
    local fn:proc;        // Declaration second (tells GAUSS it's a proc pointer)
    retp(fn(x));
endp;
```

This is a quirk of GAUSS - the parser needs to see the assignment before it knows the variable holds a function pointer.

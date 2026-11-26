# GAUSS Language Traps

Short rules that code writers and reviewers get wrong most often. Each was
checked in GAUSS 26.1.4. Read this file before writing, changing or reviewing
GAUSS code, together with the other files in `gotchas/`.

## `and` and `or` evaluate both sides

GAUSS does not short-circuit. A guard on the left does not protect the right.

```gauss
s = "abc";

// WRONG: s > 0 still runs when s is a string: G0071 Type mismatch
if type(s) == 6 and s > 0;

// RIGHT: nest the test
if type(s) == 6;
    if s > 0;
        ...
    endif;
endif;
```

## `==` and `!=` on matrices return one scalar

`a == b` is 1 only when every element is equal. `a != b` (also `/=`) is 1 only
when **every** element differs, so it misses a change in one element.

```gauss
a = { 1, 2, 3 };
b = { 1, 2, 4 };
a == b;            // 0
a != b;            // 0  -- not "they differ"
not (a == b);      // 1  -- RIGHT test for "a and b differ"
a .!= b;           // { 0, 0, 1 }  element-wise mask
```

In tests, write a difference check as `if not (a == b);` (strings:
`not (a $== b)`), never `if a != b;`.

## `not` binds weaker than `+`

`not a + b` means `not (a + b)`.

```gauss
not 1 + 1;         // 0, because not (1 + 1)
(not 1) + 1;       // 1
```

So `not (n == 8) + differs` is `not ((n == 8) + differs)`, which is 0 whenever
`differs` is 1: a failure check that can never fire. Parenthesize each term:
`(not (n == 8)) + differs`.

## `if` needs a scalar

`if x;` with a vector `x` stops with G0041 "Argument must be scalar". Reduce
the vector first:

```gauss
x = { 1, 0, 1 };
if x > 0;              // non-dot comparison: 1 only if ALL elements > 0
if sumc(x .> 0) > 0;   // any element > 0
```

## Dot operators are element-wise; plain ones reduce

`.==`, `.!=`, `.>`, `.and`, `.or` return a matrix of 0/1 (use these for
`selif`/`delif` masks). `==`, `!=`, `>`, `and`, `or` return one scalar.

```gauss
x = { 1, 0, 1 };
x .and 1;          // { 1, 0, 1 }
x > 0;             // 0
```

## Missing values compare equal

Unlike IEEE NaN, a GAUSS missing value equals itself with `==`.

```gauss
m = miss();
m == m;            // 1
ismiss(m);         // 1  -- use ismiss/packr/missrv to handle missing values
```

See `missing-values.md` for detection and removal.

## Error codes travel in the missing value

`error(n)` returns a missing value that carries code `n`; `scalerr()` reads it
back. Arithmetic on two error codes keeps only one of them:

```gauss
scalerr(error(1) + error(2));   // 2
scalerr(error(2) + error(1));   // 1
```

Check for an error code right where it is returned, before combining it with
other values.

## String comparison uses `$` operators

`$==`, `$!=`, `$+` (join), `$|` and `$~` (concatenate string arrays). Plain `==`
and `+` do not compare or join strings.

```gauss
s = "abc";
s $== "abc";       // 1
```

## String slice assignment needs the selected shape

Assigning one string to several selected rows does not broadcast (G0047,
checked in GAUSS 27). Build the replacement string array explicitly:

```gauss
x = "a" $| "b" $| "c";
idx = 1 | 3;
x[idx] = reshape("", rows(idx), 1);  // RIGHT
// x[idx] = "";                     // WRONG: Rows don't match
```

## `counts` is a reserved word

Do not use `counts` as a variable name; it produces G0276. Use a descriptive
name such as `fit_counts` (checked in GAUSS 27).

## Keyword names in a library proc must be written out

Write a keyword parameter's name literally in the `proc` line. A `#define`
name works when the file is compiled directly, but the library scanner that
autoloads procedures reads the `proc` line without expanding macros, so the
keyword is registered under the macro's name. Checked in GAUSS 27 (build 70).

```gauss
// WRONG in a library .src file: a call that autoloads minimize fails
// with G0739 Unknown keyword argument 'gradCheck'
#define GRADCHECK_KW gradCheck
proc (1) = minimize(fct, x0, method="", GRADCHECK_KW=0, ...);

// RIGHT
proc (1) = minimize(fct, x0, method="", gradCheck=0, ...);
```

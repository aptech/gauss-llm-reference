# Operator Gotchas

## Matrix vs Element-wise Multiplication

**WRONG** (LLMs do this constantly):
```gauss
result = a * b;    // This is MATRIX multiply (requires compatible dims)
```

**RIGHT**:
```gauss
result = a .* b;   // Element-wise multiply (same dimensions)
```

| Operator | Type | Example |
|----------|------|---------|
| `*` | Matrix multiply | `C = A * B` (A cols = B rows) |
| `.*` | Element-wise multiply | `C = A .* B` (same size) |
| `/` | Matrix divide (solve) | `x = b / A` solves Ax = b |
| `./` | Element-wise divide | `C = A ./ B` |
| `^` | Matrix power | `A^2` = A * A |
| `.^` | Element-wise power | `A.^2` squares each element |

## Comparison Operators

| Operator | Returns | Use When |
|----------|---------|----------|
| `==` | Scalar 1 if ALL elements equal | Checking if matrices identical |
| `.==` | 0/1 matrix (mask) | Creating masks for `selif()` |

**WRONG**:
```gauss
mask = x == 5;                    // Returns scalar, not mask!
subset = selif(data, x == 5);     // Won't work as expected
```

**RIGHT**:
```gauss
mask = x .== 5;                   // Returns 0/1 matrix
subset = selif(data, x .== 5);    // Works correctly
```

All comparison operators:
| Matrix-wide | Element-wise | Meaning |
|-------------|--------------|---------|
| `==` | `.==` | Equal |
| `!=` | `.!=` | Not equal |
| `<` | `.<` | Less than |
| `<=` | `.<=` | Less or equal |
| `>` | `.>` | Greater than |
| `>=` | `.>=` | Greater or equal |

## Logical Operators

| Operator | Type | Returns |
|----------|------|---------|
| `and` | Matrix-wide | Scalar 1 if both matrices are all non-zero |
| `or` | Matrix-wide | Scalar 1 if either matrix has any non-zero |
| `.and` | Element-wise | 0/1 matrix |
| `.or` | Element-wise | 0/1 matrix |
| `not` | Logical NOT | Inverts 0/1 |

**For combining conditions with `selif()`**, use element-wise:
```gauss
// Multiple conditions - use .and for element-wise
subset = selif(data, (data[.,"Age"] .> 18) .and (data[.,"Income"] .> 50000));
```

**WRONG**:
```gauss
// 'and' returns scalar, not useful for row-by-row filtering
subset = selif(data, (data[.,"Age"] .> 18) and (data[.,"Income"] .> 50000));
```

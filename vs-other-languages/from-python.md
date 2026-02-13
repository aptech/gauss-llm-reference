# Python/NumPy to GAUSS

## Quick Translation Table

| Python/NumPy | GAUSS | Notes |
|--------------|-------|-------|
| `a @ b` | `a * b` | Matrix multiply |
| `a * b` | `a .* b` | Element-wise multiply |
| `a / b` | `a ./ b` | Element-wise divide |
| `a ** 2` | `a .^ 2` | Element-wise power |
| `a[0, 1]` | `a[1, 2]` | GAUSS is 1-indexed |
| `a[-1]` | `a[rows(a), .]` | Last row |
| `a[mask]` | `selif(a, mask)` | Boolean selection |
| `a.T` | `a'` | Transpose |
| `np.zeros((3,4))` | `zeros(3, 4)` | |
| `np.ones((3,4))` | `ones(3, 4)` | |
| `np.eye(3)` | `eye(3)` | Identity matrix |
| `np.mean(a, axis=0)` | `meanc(a)` | Column means |
| `np.mean(a, axis=1)` | `meanr(a)` | Row means |
| `np.sum(a, axis=0)` | `sumc(a)` | Column sums |
| `np.std(a, axis=0)` | `stdc(a)` | Column std dev |
| `np.concatenate([a,b], axis=0)` | `a \| b` | Vertical stack |
| `np.concatenate([a,b], axis=1)` | `a ~ b` | Horizontal stack |
| `np.linalg.inv(a)` | `inv(a)` | Matrix inverse |
| `np.linalg.det(a)` | `det(a)` | Determinant |
| `np.linalg.eig(a)` | `{ val, vec } = eigv(a)` | Eigenvalues |
| `np.diag(a)` | `diag(a)` | Extract/create diagonal |
| `a + "b"` | `a $+ "b"` | String concat |
| `range(1, 11)` | `seqa(1, 1, 10)` or `1:10` | Sequence 1..10 |
| `# comment` | `// comment` | Comments |
| `def f(x):` | `proc (1) = f(x);` | Function def |
| `return x` | `retp(x);` | Return value |
| `if x > 0:` | `if x > 0;` | Condition (note semicolon) |
| `for i in range(10):` | `for i (1, 10, 1);` | Loop |
| `None` / `np.nan` | `miss(1,1)` | Missing value |
| `pd.read_csv("f.csv")` | `loadd("f.csv")` | Load data |

## Critical Differences

### 1. Semicolons Required
Every statement needs a semicolon:
```gauss
x = 5;           // Semicolon required
y = x + 1;       // On every line
```

### 2. Matrix Multiply is `*`, Element-wise is `.*`
```python
# Python
c = a @ b        # Matrix multiply
c = a * b        # Element-wise
```
```gauss
// GAUSS
c = a * b;       // Matrix multiply
c = a .* b;      // Element-wise
```

### 3. 1-Based Indexing
```python
# Python (0-indexed)
first = x[0]
last = x[-1]
```
```gauss
// GAUSS (1-indexed)
first = x[1];
last = x[rows(x)];
```

### 4. Boolean Selection Uses selif()
```python
# Python
subset = x[x > 0]
subset = df[df['age'] > 18]
```
```gauss
// GAUSS
subset = selif(x, x .> 0);
subset = selif(df, df[., "age"] .> 18);
```

### 5. String Operators Use $
```python
# Python
s = "a" + "b"              # "ab"
names = ["a", "b", "c"]    # list
```
```gauss
// GAUSS
s = "a" $+ "b";            // "ab"
names = "a" $| "b" $| "c"; // 3x1 string array
```

### 6. Comparison Operators
```python
# Python
mask = x > 0      # Element-wise boolean array
```
```gauss
// GAUSS
mask = x .> 0;    // Element-wise (note the dot)
// Without dot:
scalar_result = x > 0;  // True only if ALL elements > 0
```

## Common Pandas Operations

| Pandas | GAUSS |
|--------|-------|
| `df.head()` | `head(df)` |
| `df.tail()` | `tail(df)` |
| `df.shape` | `rows(df)`, `cols(df)` |
| `df.columns` | `getColNames(df)` |
| `df['col']` | `df[., "col"]` |
| `df[['a','b']]` | `df[., "a" "b"]` |
| `df.dropna()` | `packr(df)` |
| `df.fillna(0)` | `missrv(df, 0)` |
| `df.groupby('g').mean()` | `aggregate(df, "mean", "g")` |
| `df.sort_values('col')` | `sortc(df, "col")` |
| `pd.merge(a, b, on='key')` | `innerjoin(a, "key", b, "key")` |
| `pd.concat([a,b])` | `a \| b` or `dfappend(a, b)` |

## Function Definition

```python
# Python
def my_stats(x):
    mean = np.mean(x)
    std = np.std(x)
    return mean, std

m, s = my_stats(data)
```

```gauss
// GAUSS
proc (2) = myStats(x);
    local m, s;
    m = meanc(x);
    s = stdc(x);
    retp(m, s);
endp;

{ m, s } = myStats(data);
```

## Control Flow

```python
# Python
if x > 0:
    y = 1
elif x < 0:
    y = -1
else:
    y = 0

for i in range(1, 11):
    print(i)

while i < 10:
    i += 1
```

```gauss
// GAUSS
if x > 0;
    y = 1;
elseif x < 0;
    y = -1;
else;
    y = 0;
endif;

for i (1, 10, 1);
    print i;
endfor;

do while i < 10;
    i = i + 1;
endo;
```

## Common Mistakes When Coming from Python

1. **Forgetting semicolons** - Every statement needs `;`
2. **Using `*` for element-wise** - It's `.*` in GAUSS
3. **0-indexed thinking** - First element is `[1,1]` not `[0,0]`
4. **Using `+` for strings** - It's `$+` in GAUSS
5. **Boolean indexing** - Use `selif()`, not `x[mask]`
6. **Using `return`** - It's `retp()` in GAUSS
7. **Forgetting `endif`/`endfor`** - Control structures need closing keywords

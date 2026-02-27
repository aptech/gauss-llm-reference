# GAUSS Libraries and Code Organization

## Overview

GAUSS has several mechanisms for organizing and reusing code:

| Mechanism | Purpose | File Type |
|-----------|---------|-----------|
| `#include` | Copy-paste source files at compile time | `.src`, `.gss` |
| `library` | Activate libraries for autoloading | `.lcg` |
| `lib` | Build and manage library files | `.lcg` |
| `SRC_PATH` | Configure search paths | Configuration |
| Packages | Install and manage application modules | `package.json` |

## #include (Preprocessor Directive)

`#include` copies the contents of a file into your program at compile time.

```gauss
// Include a source file
#include myprocs.src

// Include with path
#include C:\gauss\myproject\utils.src

// Include from subdirectory (relative path)
#include src/helpers.src
```

### Path Resolution

GAUSS searches for included files in this order:
1. Current working directory
2. Directories in `SRC_PATH`

### #includedir

Adds directories to `SRC_PATH` at the top of your program:

```gauss
// Add the directory containing this file to SRC_PATH
#includedir

// Add a subdirectory (relative to current file)
#includedir src

// Add parent directory
#includedir ../shared
```

**Best practice:** Use `#includedir` for portable, shareable code.

### #include Gotchas

```gauss
// WRONG: Using #include at the command prompt
>> #include myfile.src    // ERROR: G0008 syntax error

// RIGHT: Use 'run' at the command prompt
>> run myfile.src;

// WRONG: Using #include with "Run Selected Text" in the IDE
// This also causes G0008 syntax error

// RIGHT: Run the entire file, or use 'run' command
```

**Key constraint:** `#include` only works inside program files, not at the interactive prompt.

## SRC_PATH (Search Paths)

`SRC_PATH` is a list of directories GAUSS searches for source files.

### Default SRC_PATH

GAUSS always includes these directories in `SRC_PATH`:

| Directory | Purpose |
|-----------|---------|
| `GAUSSHOME/src` | Core GAUSS source files |
| `GAUSSHOME/examples` | Example programs |
| `GAUSSHOME/pkgs/*/src` | All installed package source directories |

**GAUSSHOME** is the GAUSS installation directory, returned by `getGAUSSHome()`:
- macOS/Linux: `/Users/yourname/gauss26` (or `gauss25`, etc.)
- Windows: `C:\gauss26`

**Note:** If a new `GAUSSHOME/pkgs/*/src` folder is created after GAUSS starts (e.g., by installing a new package), you may need to restart GAUSS for it to be included in the path.

### Viewing SRC_PATH

```gauss
// Print current SRC_PATH
print sysstate(22, 0);

// GUI: View > Library Tool > Paths > Sources
```

### Modifying SRC_PATH at Runtime

```gauss
// Get current path
old_path = sysstate(22, 0);

// Prepend a new directory (searched first)
new_path = "C:\\myproject\\src;" $+ old_path;
call sysstate(22, new_path);

// Append a directory (searched last)
new_path = old_path $+ ";C:\\myproject\\src";
call sysstate(22, new_path);
```

Runtime changes persist until GAUSS restarts.

### Permanent Configuration (gauss.cfg)

Edit `gauss.cfg` in your GAUSSHOME directory:

```
src_path = C:\myproject\src;$(GAUSSDIR)/src;$(GAUSSDIR)/examples
```

Built-in variables for gauss.cfg:
- `$(GAUSSDIR)` - GAUSS home directory (same as `getGAUSSHome()`)
- `$(PACKAGEDIR)` - Package installation directory

## library (Loading Libraries)

The `library` statement activates libraries for procedure autoloading.

```gauss
// Show current active libraries
library;

// Activate a single library
library pgraph;

// Activate multiple libraries
library tsmt, cmlmt, maxlik;
```

### How Autoloading Works

1. You call a procedure that isn't currently loaded
2. GAUSS searches active library files (`.lcg`)
3. Finds which `.src` file contains the procedure
4. Automatically loads that source file
5. Executes your procedure call

### Library Search Order

1. `user.lcg` (always first)
2. User-specified libraries (in order declared)
3. `gauss.lcg` (always last)

### Default Libraries

`user` and `gauss` libraries are always active unless explicitly replaced:

```gauss
// This replaces all optional libraries but keeps user and gauss
library mylib;

// This replaces everything including user and gauss (rarely needed)
library -force mylib;
```

## Library Files (.lcg)

Library files are plain text files mapping source files to symbols.

### LCG File Format

```
/*
** Library comment header
*/

sourcefile.src
    symbolName                       : type : lineNumber
    anotherSymbol                    : type : lineNumber

/full/path/to/otherfile.src
    myProc                           : proc : 25
```

**Format details:**
- Source file on its own line (relative or absolute path)
- Symbols indented below their source file
- Symbol format: `name : type : line` (line number is optional)
- Comments: `/*`, `**`, or `*/`

### Symbol Types in LCG Files

| Type | Description | Source File |
|------|-------------|-------------|
| `proc` | Procedure | `.src` |
| `fn` | Single-line function | `.src` |
| `keyword` | Keyword procedure | `.src` |
| `matrix` | Matrix variable | `.dec` |
| `string` | String variable | `.dec` |
| `array` | Array variable | `.dec` |
| `definition` | Structure definition | `.sdf` |

### Source File Types

| Extension | Purpose |
|-----------|---------|
| `.src` | Procedure source code |
| `.sdf` | Structure definitions (`struct`) |
| `.dec` | Variable declarations (globals) |
| `.ext` | External declarations |
| `.gss` | GAUSS script (main programs) |

### Example LCG File

```
/*
** My Custom Library
** Version: 1.0.0
*/

stats.src
    meanTrim                         : proc : 25
    medianAbs                        : proc : 48
    _statsVersion                    : string : 10

stats.sdf
    struct statsControl                     : definition : 15
    struct statsOut                         : definition : 42

io.src
    loadConfig                       : proc : 12
    saveResults                      : proc : 67
```

### Real-World Example (from gauss.lcg)

```
aggregate.src
    aggregate                        : proc : 25

cdfchii.src
    cdfchii                          : proc : 47
    gammaii                          : proc : 75
    _ginvinc                         : proc : 134

contingency.sdf
    struct contingencyControl               : definition : 20
    struct contingencyOut                    : definition : 32
```

## lib (Library Management Command)

The `lib` command builds and manages `.lcg` files.

### Basic Operations

```gauss
// Add/update a file in a library
lib mylib myprocs.src;

// List library contents
lib mylib -list;

// Rebuild all symbol information
lib mylib -build;

// Remove a file from library
lib mylib myprocs.src -delete;

// Update symbols for one file
lib mylib myprocs.src -update;
```

### Creating a New Library

```gauss
// Add first file (creates library if needed)
lib mylib myprocs.src;

// Add more files
lib mylib utils.src;
lib mylib stats.src;

// Verify contents
lib mylib -list;
```

### Path Handling Flags

| Flag | Purpose |
|------|---------|
| `-addpath` | Add full paths to entries |
| `-gausspath` | Reset paths using standard search |
| `-leavepath` | Preserve existing paths (default) |
| `-nopath` | Strip all path information |

### Symbol Type Flags

| Flag | Purpose |
|------|---------|
| `-strong` | Keep type info (default) |
| `-weak` | Omit types (backward compatibility) |

Flags can be abbreviated: `-b` for `-build`, `-l` for `-list`.

## Packages

Packages are pre-built collections of procedures for specific domains (time series, optimization, etc.). They include source code, examples, documentation, and a library file.

### Installing Packages

**Package Manager (preferred):**
1. Go to **Tools > Package Manager**
2. Click the plus icon to view available packages
3. Select a package and click **Install Package**

**Applications Installer (fallback):**
1. Download the package `.zip` file
2. Go to **Tools > Install Application**
3. Navigate to the downloaded file

### Package Structure

**Before installation** (what you distribute):

```
mypackage/
├── package.json       # Package metadata (required)
├── src/               # Source files (.src, .sdf, .dec)
├── examples/          # Example programs (optional)
└── docs/              # Documentation (optional)
```

**After installation** (in `GAUSSHOME/pkgs/packagename/`):

```
GAUSSHOME/
└── pkgs/
    └── mypackage/
        ├── package.json
        ├── src/
        ├── lib/
        │   └── mypackage.lcg  # AUTO-GENERATED by installer
        ├── examples/
        └── docs/
```

**Key points:**
- You don't create the `.lcg` file - the **Applications Installer** generates it automatically from `package.json`
- Source files in `GAUSSHOME/pkgs/*/src` are **always in SRC_PATH**, so autoloading just works
- May need to restart GAUSS after installing a new package if the folder didn't exist at startup

### package.json Format

```json
{
    "name": "tsmt",
    "version": "4.0.0",
    "author": "Aptech Systems",
    "description": "Time series for GAUSS",
    "license": "GAUSS Standard License Agreement",
    "src": [
        "tsmt.dec",
        "tsmt.sdf",
        "arimamt.src",
        "autoregmt.src"
    ],
    "deps": [],
    "dlib": []
}
```

The `src` array is the manifest - it tells the installer which files to include in the generated `.lcg`.

### Using Packages

```gauss
// Load the package library
library tsmt;

// Now you can use package procedures
struct arimamtOut out;
out = arimamt(y, p, d, q);
```

### Common Packages

| Package | Description | Type |
|---------|-------------|------|
| `tsmt` | Time Series MT | Commercial |
| `cmlmt` | Constrained Maximum Likelihood | Commercial |
| `comt` | Constrained Optimization | Commercial |
| `maxlik` | Maximum Likelihood | Included |
| `pgraph` | Publication Graphics | Included |
| `dc` | Discrete Choice | Commercial |

### Viewing Installed Packages

```gauss
// List installed packages via GUI
// Tools > Package Manager

// Or check the pkgs directory
filesa(getGAUSSHome() $+ "/pkgs/*");
```

## Legacy Packages (Pre-Package Manager)

Older GAUSS packages (pre-2010) don't have `package.json` and require manual setup. They typically have:

- **Relative paths in LCG** - No full paths to source files
- **No line numbers** - Just `symbol : type` format
- **Source files in non-standard locations** - Not in `SRC_PATH`
- **Manual installation** - Batch scripts or README instructions

### Legacy Package Structure

```
tsm/                           # Old-style package
├── lib/
│   └── TSM.LCG               # Library with relative paths only
├── srctsm/                    # Source files (non-standard location)
│   ├── ARMA1.SRC
│   ├── KALMAN$.SRC
│   └── TSM.DEC
├── README.TSM                 # Manual installation instructions
└── ginstall.bat               # Old installer script
```

### Legacy LCG Format

Old LCG files have relative paths and no line numbers:

```
arma1.src
    arma_ml                          : proc
    arma_cml                         : proc

kalman$.src
    ssm_build                        : proc
    kfiltering                       : proc

tsm.dec
    _tsm_ver                         : matrix
    _print                           : matrix
```

### The Problem

When GAUSS tries to autoload a procedure:
1. Finds `arma1.src` in the LCG
2. Searches current directory - not there
3. Searches `SRC_PATH` - source directory isn't in it
4. **Autoload fails**

### Solutions for Legacy Packages

**Option 1: Rebuild LCG with full paths (recommended)**
```gauss
// Navigate to source directory FIRST
chdir /path/to/package/srctsm;

// THEN rebuild with absolute paths
lib PACKAGENAME -build -addpath;
```

**CRITICAL: You must be in the source directory (or have it in SRC_PATH) when running `-addpath`.**

The `-addpath` flag adds the path *where the file was found*. If GAUSS can't find the files, the rebuild fails or removes entries from the library:

```gauss
// WRONG: Source files not findable from here
chdir /some/other/directory;
lib TSM -build -addpath;    // FAILS or EMPTIES the library!

// RIGHT: Navigate to source directory first
chdir /path/to/package/srctsm;
lib TSM -build -addpath;    // Works - finds files in current directory
```

This is why legacy README files always instruct you to `chdir` to the source directory before running `lib -a`.

**Option 2: Add source directory to SRC_PATH**
```gauss
// At runtime
new_path = "/path/to/package/srctsm;" $+ sysstate(22, 0);
call sysstate(22, new_path);

// Or in your program
#includedir /path/to/package/srctsm
```

**Option 3: Add to gauss.cfg permanently**
```
src_path = /path/to/package/srctsm;$(GAUSSDIR)/src
```

### Identifying Legacy Packages

Check for these signs:
- No `package.json` file
- LCG has relative filenames (no `/` or `\` in paths)
- LCG has no line numbers (just `name : type`)
- README mentions manual `lib -a` or `chdir` steps
- Source files in custom directory (not `src/`)

### Converting Legacy to Modern Format

To modernize a legacy package:

1. **Create `package.json`** with source file list:
   ```json
   {
       "name": "tsm",
       "version": "1.2.12",
       "author": "Original Author",
       "description": "Time Series Modeling",
       "src": ["arma1.src", "arma2.src", "tsm.dec"]
   }
   ```

2. **Move source files to `src/` directory**

3. **Optionally add `examples/` directory** with example programs

4. **Delete the old `.lcg` file** - the installer will generate a new one

5. **Install via Tools > Install Application** - this generates the `.lcg` automatically with full paths and line numbers

No manual `lib` commands needed - the installer handles everything based on `package.json`.

## Common Patterns

### Project Structure

```
myproject/
├── main.gss           # Main program
├── src/
│   ├── analysis.src   # Analysis procedures
│   ├── io.src         # I/O procedures
│   └── utils.src      # Utility procedures
├── lib/
│   └── myproject.lcg  # Library file
└── data/
    └── input.csv
```

### Simple Project (Using #include)

```gauss
// main.gss
#includedir src

#include utils.src
#include io.src
#include analysis.src

// Your main code here
data = loadData("data/input.csv");
results = runAnalysis(data);
```

### Larger Project (Using Libraries)

```gauss
// First, build the library (run once or when code changes)
lib myproject src/analysis.src;
lib myproject src/io.src;
lib myproject src/utils.src;

// In your main program
library myproject;

// Procedures autoload when called
data = loadData("data/input.csv");
results = runAnalysis(data);
```

### Hybrid Approach

```gauss
// main.gss

// Use library for stable, shared code
library myutils;

// Use #include for project-specific code under development
#includedir src
#include analysis.src

// Your code here
```

## #include vs library

| Aspect | #include | library |
|--------|----------|---------|
| When loaded | Compile time | Runtime (on demand) |
| Memory | All code loaded upfront | Only loads what's needed |
| Rebuild | Recompile to pick up changes | Automatic with autoload |
| Setup | None | Must create .lcg file |
| Best for | Small projects, local code | Large projects, shared code |

### When to Use Each

**Use `#include` when:**
- Small project with few files
- Code is specific to one program
- You want simple, self-contained programs
- Sharing code via copy (all in one file)

**Use `library` when:**
- Large codebase with many procedures
- Code shared across multiple programs
- Memory efficiency matters
- Team development with shared libraries

## Troubleshooting

### Common Error Messages

| Error | Meaning | Likely Cause | Solution |
|-------|---------|--------------|----------|
| `Undefined symbol: procname` | Procedure not found | Library not loaded, or source files not in `SRC_PATH` | Load library with `library libname;` or add source directory to `SRC_PATH` |
| `G0014: File not found` | `#include` can't find file | File not in current directory or `SRC_PATH` | Use `#includedir` or add directory to `SRC_PATH` |
| `G0024: Library not found` | `library` can't find `.lcg` file | LCG file not in `LIB_PATH` | Check `sysstate(21, 0)` and add library directory |
| `G0008: Syntax error` (with `#include`) | Using `#include` at command prompt | `#include` only works in program files | Use `run filename.src;` at command prompt instead |

### Debugging Steps for "Undefined symbol" Errors

1. **Is the library loaded?**
   ```gauss
   library;    // Shows active libraries
   ```

2. **Is the library file findable?**
   ```gauss
   print sysstate(21, 0);    // Show LIB_PATH
   ```

3. **Are source files findable?**
   ```gauss
   print sysstate(22, 0);    // Show SRC_PATH
   ```

4. **Does the LCG have full paths?**
   ```gauss
   lib mylib -list;    // Check if paths are relative or absolute
   ```

5. **For legacy packages:** Source files may not be in `SRC_PATH`. See [Legacy Packages](#legacy-packages-pre-package-manager) section.

### Quick Fixes

**Undefined symbol after loading library:**
```gauss
// Check if source directory is in path
print sysstate(22, 0);

// If not, add it temporarily
call sysstate(22, "/path/to/src;" $+ sysstate(22, 0));

// Or rebuild library with full paths (from source directory)
chdir /path/to/src;
lib mylib -build -addpath;
```

**Library not found:**
```gauss
// Check library path
print sysstate(21, 0);

// Add library directory
call sysstate(21, "/path/to/lib;" $+ sysstate(21, 0));
```

## Gotchas

```gauss
// WRONG: #include at command prompt
>> #include myfile.src     // ERROR

// RIGHT: use run at command prompt
>> run myfile.src;

// WRONG: Forgetting library path isn't in lib_path
library mylib;             // G0024: Library not found

// RIGHT: Check lib_path or use full path
print sysstate(21, 0);     // Print lib_path

// WRONG: Assuming library picks up code changes automatically
// If you edit a .src file, the library may have old symbol info

// RIGHT: Rebuild after code changes
lib mylib -build;

// WRONG: Circular includes
// file1.src: #include file2.src
// file2.src: #include file1.src   // Infinite loop!

// RIGHT: Organize includes hierarchically
// utils.src: no includes
// analysis.src: #include utils.src
// main.gss: #include analysis.src
```

## Related Configuration

### Viewing All Paths

```gauss
// SRC_PATH (source files)
print sysstate(22, 0);

// LIB_PATH (library files)
print sysstate(21, 0);

// Current working directory
print cwd;
```

### Path Separators

- Windows: Use `;` between paths, `\` or `/` in paths
- macOS/Linux: Use `:` between paths, `/` in paths

```gauss
// Windows
new_path = "C:\\project1\\src;C:\\project2\\src";

// macOS/Linux
new_path = "/home/user/project1/src:/home/user/project2/src";
```

## Quick Reference

| Task | Command |
|------|---------|
| Include source file | `#include file.src` |
| Add dir to SRC_PATH | `#includedir dirname` |
| View SRC_PATH | `print sysstate(22, 0);` |
| Modify SRC_PATH | `call sysstate(22, newpath);` |
| View active libraries | `library;` |
| Activate library | `library mylib;` |
| List library contents | `lib mylib -list;` |
| Add file to library | `lib mylib file.src;` |
| Rebuild library | `lib mylib -build;` |
| View LIB_PATH | `print sysstate(21, 0);` |
| Install package | Tools > Package Manager |
| Get GAUSS home path | `getGAUSSHome()` |
| Run source file | `run myfile.src;` |

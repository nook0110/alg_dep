# Polynomial Algebraic Dependency Checker - Implementation Plan

## Project Overview

A Python program to analyze polynomial pairs (f, g) ∈ Z[x,y] to find algebraic dependencies q(x, f, g) = 0 and verify divisibility conditions.

## Key Requirements Met

✅ **Brute Force with State Persistence**: System saves progress and resumes after restart  
✅ **Manual Check Mode**: Test specific polynomial pairs  
✅ **Result Caching**: Avoid recomputation of already-checked pairs  
✅ **Configurable Parameters**: Adjustable max degrees, coefficient ranges, enumeration strategies  
✅ **Input Format**: Parse polynomials like `x^2 + y^2 - 1`  

## System Architecture

### Core Components

1. **Configuration Manager** - Centralized parameter management
2. **Polynomial Parser** - Parse string format `x^2 + y^2` into internal representation
3. **Polynomial Operations** - Derivatives, substitution, divisibility checking
4. **Polynomial Generator** - Enumerate (f, g) pairs with configurable strategies
5. **Dependency Finder** - Find q where q(x, f, g) = 0
6. **Divisibility Checker** - Verify ∂q/∂f : ∂q/∂x and ∂q/∂g : ∂q/∂x
7. **State Manager** - Save/restore brute force progress (JSON)
8. **Result Cache** - SQLite database for persistent results
9. **CLI Interface** - Command-line interface for all operations

### Data Flow

```
User Input → Parser → Polynomial Objects
                           ↓
                    Check Cache → Found? Return Result
                           ↓ Not Found
                    Dependency Finder → Find q
                           ↓
                    Divisibility Checker → Check conditions
                           ↓
                    Save to Cache → Update State
```

## File Structure

```
alg_dep/
├── src/
│   ├── config.py              # Configuration
│   ├── polynomial.py          # Core data structure
│   ├── parser.py              # String → Polynomial
│   ├── operations.py          # Math operations
│   ├── generator.py           # Enumerate pairs
│   ├── dependency_finder.py   # Find q(x,f,g)=0
│   ├── divisibility.py        # Check divisibility
│   ├── state.py               # State persistence
│   ├── cache.py               # Result storage
│   ├── brute_force.py         # Brute force runner
│   ├── manual_check.py        # Manual checker
│   └── cli.py                 # CLI interface
├── tests/                     # Unit tests
├── data/                      # Runtime data
│   ├── results.db            # SQLite cache
│   └── state.json            # Progress state
├── ARCHITECTURE.md           # Detailed design
└── README.md                 # User guide
```

## Key Features

### 1. Configurable Enumeration
- **Max Degrees**: Separate limits for f, g, and q
- **Coefficient Range**: Min/max values (e.g., -2 to 2)
- **Strategies**: Lexicographic or degree-first enumeration
- **Filtering**: Skip trivial cases (e.g., both constant)

### 2. State Persistence
- **Checkpoint System**: Save progress every N pairs
- **Resume Capability**: Continue from last checkpoint after restart
- **Progress Tracking**: Count total pairs, pairs with dependencies

### 3. Result Caching
- **SQLite Database**: Persistent storage across runs
- **Hash-based Lookup**: Fast retrieval by polynomial hash
- **Avoid Recomputation**: Check cache before processing
- **Query Interface**: Search results by conditions

### 4. CLI Interface

```bash
# Brute force mode
python -m src.cli brute --max-degree-f 3 --max-degree-g 3 --max-degree-q 4

# Resume from checkpoint
python -m src.cli brute --resume

# Manual check
python -m src.cli check "x^2 + y^2" "x*y"

# Statistics
python -m src.cli stats

# Query results
python -m src.cli query --both-divisible
```

## Implementation Phases

### Phase 1: Core Infrastructure
- [ ] Polynomial representation and hashing
- [ ] Parser for `x^2 + y^2` format
- [ ] Basic operations (add, multiply, substitute)
- [ ] Configuration system

### Phase 2: Mathematical Operations
- [ ] Partial derivatives
- [ ] Polynomial division and divisibility
- [ ] Dependency finding algorithm
- [ ] Divisibility checker

### Phase 3: Enumeration System
- [ ] Polynomial generator with strategies
- [ ] Configurable degree and coefficient bounds
- [ ] Pair generation with filtering

### Phase 4: Persistence Layer
- [ ] SQLite result cache
- [ ] State manager with JSON serialization
- [ ] Checkpoint system

### Phase 5: User Interface
- [ ] CLI with argparse
- [ ] Brute force runner
- [ ] Manual check mode
- [ ] Statistics and query commands

### Phase 6: Testing & Documentation
- [ ] Unit tests for each module
- [ ] Integration tests
- [ ] User documentation
- [ ] Example usage

## Technical Decisions

### Why SQLite?
- Lightweight, no separate server
- ACID transactions
- Fast indexed lookups
- Portable single-file database

### Why JSON for State?
- Human-readable
- Easy to inspect/debug
- Simple serialization
- Small file size

### Why SymPy?
- Robust symbolic computation
- Polynomial operations built-in
- Well-tested and maintained
- Python integration

## Next Steps

1. **Review this plan** - Ensure it meets your requirements
2. **Adjust if needed** - Modify degrees, strategies, or features
3. **Switch to Code mode** - Begin implementation
4. **Iterative development** - Build and test incrementally

## Questions for Review

1. Is the enumeration strategy (lexicographic/degree-first) suitable?
2. Are the default degree limits (f,g: 2, q: 3) appropriate?
3. Should we add parallel processing for brute force?
4. Any additional output formats needed (CSV, JSON export)?
5. Should we support more than 2 variables (x, y)?

---

**Ready to proceed?** If you approve this plan, I'll switch to Code mode to begin implementation.
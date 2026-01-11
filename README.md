# Polynomial Algebraic Dependency Checker

A Python tool to analyze polynomial pairs (f, g) ∈ Z[x,y] to find algebraic dependencies q(x, f, g) = 0 and verify divisibility conditions.

## Features

✅ **Brute Force Mode**: Systematically enumerate and check polynomial pairs  
✅ **Manual Check Mode**: Test specific polynomial pairs  
✅ **State Persistence**: Resume interrupted searches from checkpoints  
✅ **Result Caching**: SQLite database prevents recomputation  
✅ **Configurable**: Adjustable degrees, coefficient ranges, enumeration strategies  
✅ **Simple Syntax**: Input polynomials like `x^2 + y^2 - 1`  

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd alg_dep

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Check a Specific Polynomial Pair

```bash
python run.py check "x^2 + y^2" "x*y"
```

### Run Brute Force Search

```bash
# Start with default settings (4 workers)
python run.py brute

# Custom parameters with 8 parallel workers
python run.py brute --max-degree-f 3 --max-degree-g 3 --max-degree-q 4 --workers 8

# Resume from checkpoint
python run.py brute --resume
```

### View Statistics

```bash
python run.py stats
```

### Query Results

```bash
# Show all results
python run.py query

# Show only pairs where both divisibility conditions hold
python run.py query --both-divisible
```

## Mathematical Background

For each pair of polynomials (f, g) ∈ Z[x,y], the program:

1. **Finds dependency**: Searches for polynomial q ∈ Q[x,u,v] such that q(x, f(x,y), g(x,y)) = 0
   - Uses multiple algorithms: trivial checks, Gröbner basis, interpolation, and brute force
2. **Checks divisibility**: Verifies if:
   - ∂q/∂u is divisible by ∂q/∂x (where u represents f)
   - ∂q/∂v is divisible by ∂q/∂x (where v represents g)

### Dependency Finding Algorithms

The system uses a multi-strategy approach (in order of execution):

1. **Resultant Method** (Primary): Uses resultants to eliminate y algebraically
   - Computes Res_y(u - f(x,y), v - g(x,y))
   - Produces polynomial in Q[x,u,v] directly
   - Fast and mathematically elegant

2. **Gröbner Basis Method** (Backup): Uses elimination ideals
   - Computes Gröbner basis with elimination order
   - Finds polynomials in Q[x,u,v]

3. **Brute Force** (Fallback): Exhaustive search over all polynomials up to max degree
   - Guaranteed completeness within degree bounds

This multi-algorithm approach ensures both speed and mathematical correctness.

## Usage Examples

### Example 1: Manual Check

```bash
$ python run.py check "x^2 + y^2" "x*y"

============================================================
MANUAL CHECK
============================================================
f = x^2 + y^2
g = x*y

Parsed f = x**2 + y**2
Parsed g = x*y

Searching for dependency q(x, u, v) where q(x, f, g) = 0...
Max degree for q: 3

✓ Found dependency:
  q = u - x**2 - y**2

Checking divisibility conditions...
  ∂q/∂u : ∂q/∂x = False
  ∂q/∂v : ∂q/∂x = True

✗ Not all divisibility conditions satisfied.

Result saved to cache.
```

### Example 2: Brute Force with Custom Parameters

```bash
$ python run.py brute --max-degree-f 2 --max-degree-g 2 --max-degree-q 3 --coeff-min -1 --coeff-max 1

Starting brute force search...
Configuration:
  Max degree f: 2
  Max degree g: 2
  Max degree q: 3
  Coefficient range: [-1, 1]
  Strategy: lexicographic

[CHECKING] f=0, g=0
  No dependency found
[CHECKING] f=0, g=1
  No dependency found
...
```

### Example 3: View Statistics

```bash
$ python run.py stats

============================================================
STATISTICS
============================================================
Total pairs checked: 150
Pairs with dependency: 45
Pairs with both conditions satisfied: 12

Percentages:
  With dependency: 30.0%
  Both conditions: 8.0%
```

## Command Reference

### `brute` - Brute Force Mode

Run systematic enumeration of polynomial pairs.

```bash
python run.py brute [OPTIONS]
```

**Options:**
- `--max-degree-f N`: Maximum degree for polynomial f (default: 2)
- `--max-degree-g N`: Maximum degree for polynomial g (default: 2)
- `--max-degree-q N`: Maximum degree for dependency q (default: 3)
- `--coeff-min N`: Minimum coefficient value (default: -2)
- `--coeff-max N`: Maximum coefficient value (default: 2)
- `--strategy {lexicographic,degree_first}`: Enumeration strategy (default: lexicographic)
- `--checkpoint-interval N`: Save state every N pairs (default: 10)
- `--resume`: Resume from last checkpoint

### `check` - Manual Check Mode

Check a specific polynomial pair.

```bash
python run.py check F G [OPTIONS]
```

**Arguments:**
- `F`: First polynomial (e.g., "x^2 + y^2")
- `G`: Second polynomial (e.g., "x*y")

**Options:**
- `--max-degree-q N`: Maximum degree for dependency q (default: 3)
- `--coeff-min N`: Minimum coefficient value (default: -2)
- `--coeff-max N`: Maximum coefficient value (default: 2)

### `stats` - Statistics

Show summary statistics from the result cache.

```bash
python run.py stats
```

### `query` - Query Results

Query and display results from the cache.

```bash
python run.py query [OPTIONS]
```

**Options:**
- `--both-divisible`: Show only pairs where both conditions hold
- `--limit N`: Maximum number of results to show (default: 20)

## Input Format

Polynomials are entered as strings using standard mathematical notation:

- **Variables**: `x` and `y`
- **Exponentiation**: `x^2` or `x**2`
- **Multiplication**: `x*y` or `2*x` (implicit multiplication like `2x` may not work)
- **Addition/Subtraction**: `x + y`, `x - y`
- **Examples**:
  - `x^2 + y^2`
  - `x*y - 1`
  - `2*x^2 + 3*x*y - y^2`

## Data Storage

The program stores data in the `data/` directory:

- **`data/results.db`**: SQLite database with all results
- **`data/state.json`**: Checkpoint state for brute force

These files are created automatically on first run.

## Configuration

Default configuration can be modified in [`src/config.py`](src/config.py:1):

```python
@dataclass
class Config:
    max_degree_f: int = 2
    max_degree_g: int = 2
    max_degree_q: int = 3
    coeff_min: int = -2
    coeff_max: int = 2
    enum_strategy: str = "lexicographic"
    checkpoint_interval: int = 10
```

## Architecture

The system consists of modular components:

- **[`polynomial.py`](src/polynomial.py:1)**: SymPy-based polynomial operations
- **[`generator.py`](src/generator.py:1)**: Polynomial pair enumeration
- **[`dependency_finder.py`](src/dependency_finder.py:1)**: Find q(x,f,g)=0
- **[`divisibility.py`](src/divisibility.py:1)**: Check divisibility conditions
- **[`cache.py`](src/cache.py:1)**: SQLite result storage
- **[`state.py`](src/state.py:1)**: JSON state persistence
- **[`brute_force.py`](src/brute_force.py:1)**: Brute force runner
- **[`manual_check.py`](src/manual_check.py:1)**: Manual checker
- **[`cli.py`](src/cli.py:1)**: Command-line interface

See [`ARCHITECTURE.md`](ARCHITECTURE.md:1) for detailed design documentation.

## Performance Considerations

- **Computational Complexity**: Grows exponentially with degree and coefficient range
- **Caching**: Always checks cache before computation
- **Checkpointing**: Saves state regularly to allow resume
- **Interruption**: Press Ctrl+C to safely interrupt and save progress

## Troubleshooting

### "No module named 'sympy'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### Brute force is too slow

Reduce the search space:
```bash
python -m src.cli brute --max-degree-f 1 --max-degree-g 1 --coeff-min -1 --coeff-max 1
```

### Want to clear cache and start fresh

Delete the data directory:
```bash
rm -rf data/
```

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
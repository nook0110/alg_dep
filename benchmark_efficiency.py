#!/usr/bin/env python3
"""Benchmark script to measure efficiency of dependency finding."""

import time
import sys
from src.config import Config
from src.generator import PolynomialGenerator
from src.dependency_finder import DependencyFinder
from src.divisibility import DivisibilityChecker


def benchmark_single_pair(config: Config, f, g):
    """
    Benchmark a single pair and return timing information.
    
    Args:
        config: Configuration object
        f: First polynomial
        g: Second polynomial
        
    Returns:
        Dictionary with timing and result information
    """
    finder = DependencyFinder(config)
    checker = DivisibilityChecker()
    
    start_time = time.time()
    q, was_trivial = finder.find_dependency(f, g)
    find_time = time.time() - start_time
    
    divisibility = {}
    check_time = 0.0
    if q:
        start_check = time.time()
        divisibility = checker.check_conditions(q, f, g)
        check_time = time.time() - start_check
    
    total_time = find_time + check_time
    
    return {
        'f': str(f),
        'g': str(g),
        'q': str(q) if q else None,
        'was_trivial': was_trivial,
        'find_time': find_time,
        'check_time': check_time,
        'total_time': total_time,
        'divisibility': divisibility
    }


def run_benchmark(config: Config, num_samples: int = 10):
    """
    Run benchmark on multiple pairs and compute statistics.
    
    Args:
        config: Configuration object
        num_samples: Number of pairs to benchmark
    """
    print("="*80)
    print("EFFICIENCY BENCHMARK")
    print("="*80)
    print(f"\nConfiguration:")
    print(f"  Max degree f: {config.max_degree_f}")
    print(f"  Max degree g: {config.max_degree_g}")
    print(f"  Max degree q: {config.max_degree_q}")
    print(f"  Coefficient range: [{config.coeff_min}, {config.coeff_max}]")
    print(f"  Strategy: {config.enum_strategy}")
    print(f"  Number of samples: {num_samples}")
    print()
    
    generator = PolynomialGenerator(config)
    results = []
    
    print("Processing pairs...")
    print("-"*80)
    
    for i, (f, g) in enumerate(generator.generate_pairs()):
        if i >= num_samples:
            break
        
        result = benchmark_single_pair(config, f, g)
        results.append(result)
        
        print(f"\nPair #{i+1}:")
        print(f"  f = {result['f']}")
        print(f"  g = {result['g']}")
        if result['q']:
            status = "TRIVIAL" if result['was_trivial'] else "NON-TRIVIAL"
            print(f"  q = {result['q']} [{status}]")
            if result['divisibility']:
                print(f"  ∂q/∂f : ∂q/∂x = {result['divisibility'].get('df_divisible', False)}")
                print(f"  ∂q/∂g : ∂q/∂x = {result['divisibility'].get('dg_divisible', False)}")
        else:
            print(f"  q = None (no dependency found)")
        print(f"  Time to find dependency: {result['find_time']:.4f}s")
        if result['check_time'] > 0:
            print(f"  Time to check divisibility: {result['check_time']:.4f}s")
        print(f"  Total time: {result['total_time']:.4f}s")
    
    # Compute statistics
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    
    total_times = [r['total_time'] for r in results]
    find_times = [r['find_time'] for r in results]
    check_times = [r['check_time'] for r in results if r['check_time'] > 0]
    
    with_dependency = [r for r in results if r['q'] is not None]
    nontrivial = [r for r in with_dependency if not r['was_trivial']]
    trivial = [r for r in with_dependency if r['was_trivial']]
    
    print(f"\nPairs processed: {len(results)}")
    print(f"  With dependency: {len(with_dependency)} ({len(with_dependency)/len(results)*100:.1f}%)")
    print(f"    - Non-trivial: {len(nontrivial)}")
    print(f"    - Trivial: {len(trivial)}")
    print(f"  Without dependency: {len(results) - len(with_dependency)}")
    
    print(f"\nTiming Statistics:")
    print(f"  Average time per pair: {sum(total_times)/len(total_times):.4f}s")
    print(f"  Min time: {min(total_times):.4f}s")
    print(f"  Max time: {max(total_times):.4f}s")
    print(f"  Total time: {sum(total_times):.4f}s")
    
    print(f"\nDependency Finding:")
    print(f"  Average time: {sum(find_times)/len(find_times):.4f}s")
    print(f"  Min time: {min(find_times):.4f}s")
    print(f"  Max time: {max(find_times):.4f}s")
    
    if check_times:
        print(f"\nDivisibility Checking (when dependency found):")
        print(f"  Average time: {sum(check_times)/len(check_times):.4f}s")
        print(f"  Min time: {min(check_times):.4f}s")
        print(f"  Max time: {max(check_times):.4f}s")
    
    # Estimate total time for all pairs
    total_pairs = generator.count_total_pairs()
    avg_time = sum(total_times) / len(total_times)
    estimated_total = total_pairs * avg_time
    
    print(f"\nProjection:")
    print(f"  Total pairs to check: {total_pairs}")
    print(f"  Estimated total time: {estimated_total:.2f}s ({estimated_total/60:.2f}min, {estimated_total/3600:.2f}h)")
    print(f"  With {config.num_workers} workers: {estimated_total/config.num_workers:.2f}s ({estimated_total/config.num_workers/60:.2f}min, {estimated_total/config.num_workers/3600:.2f}h)")
    
    # Divisibility statistics for non-trivial dependencies
    if nontrivial:
        both_div = sum(1 for r in nontrivial 
                      if r['divisibility'].get('df_divisible') and r['divisibility'].get('dg_divisible'))
        df_only = sum(1 for r in nontrivial 
                     if r['divisibility'].get('df_divisible') and not r['divisibility'].get('dg_divisible'))
        dg_only = sum(1 for r in nontrivial 
                     if not r['divisibility'].get('df_divisible') and r['divisibility'].get('dg_divisible'))
        neither = len(nontrivial) - both_div - df_only - dg_only
        
        print(f"\nDivisibility Results (non-trivial dependencies only):")
        print(f"  Both conditions satisfied: {both_div}/{len(nontrivial)} ({both_div/len(nontrivial)*100:.1f}%)")
        print(f"  Only ∂q/∂f : ∂q/∂x: {df_only}/{len(nontrivial)} ({df_only/len(nontrivial)*100:.1f}%)")
        print(f"  Only ∂q/∂g : ∂q/∂x: {dg_only}/{len(nontrivial)} ({dg_only/len(nontrivial)*100:.1f}%)")
        print(f"  Neither condition: {neither}/{len(nontrivial)} ({neither/len(nontrivial)*100:.1f}%)")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Benchmark efficiency of dependency finding"
    )
    parser.add_argument('--max-degree-f', type=int, default=3,
                       help='Maximum degree for polynomial f (default: 3)')
    parser.add_argument('--max-degree-g', type=int, default=3,
                       help='Maximum degree for polynomial g (default: 3)')
    parser.add_argument('--max-degree-q', type=int, default=4,
                       help='Maximum degree for dependency q (default: 4)')
    parser.add_argument('--coeff-min', type=int, default=-2,
                       help='Minimum coefficient value (default: -2)')
    parser.add_argument('--coeff-max', type=int, default=2,
                       help='Maximum coefficient value (default: 2)')
    parser.add_argument('--samples', type=int, default=10,
                       help='Number of pairs to benchmark (default: 10)')
    parser.add_argument('--workers', type=int, default=4,
                       help='Number of workers for projection (default: 4)')
    
    args = parser.parse_args()
    
    config = Config(
        max_degree_f=args.max_degree_f,
        max_degree_g=args.max_degree_g,
        max_degree_q=args.max_degree_q,
        coeff_min=args.coeff_min,
        coeff_max=args.coeff_max,
        num_workers=args.workers
    )
    
    try:
        run_benchmark(config, args.samples)
    except KeyboardInterrupt:
        print("\n\nBenchmark interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
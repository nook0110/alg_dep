import argparse
import sys
import logging
from tabulate import tabulate

from .config import Config
from .brute_force import BruteForceRunner
from .manual_check import ManualChecker
from .cache import ResultCache

logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    parser = argparse.ArgumentParser(
        description="Polynomial Algebraic Dependency Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run brute force search
  python -m src.cli brute
  
  # Run with custom parameters
  python -m src.cli brute --max-degree-f 3 --max-degree-g 3 --max-degree-q 4
  
  # Resume from checkpoint
  python -m src.cli brute --resume
  
  # Check specific polynomial pair
  python -m src.cli check "x^2 + y^2" "x*y"
  
  # Show statistics
  python -m src.cli stats
  
  # Query results
  python -m src.cli query --both-divisible
        """
    )
    
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Brute force mode
    brute_parser = subparsers.add_parser('brute', help='Run brute force search')
    brute_parser.add_argument('--max-degree-f', type=int, default=2,
                             help='Maximum degree for polynomial f (default: 2)')
    brute_parser.add_argument('--max-degree-g', type=int, default=2,
                             help='Maximum degree for polynomial g (default: 2)')
    brute_parser.add_argument('--max-degree-q', type=int, default=3,
                             help='Maximum degree for dependency q (default: 3)')
    brute_parser.add_argument('--coeff-min', type=int, default=-2,
                             help='Minimum coefficient value (default: -2)')
    brute_parser.add_argument('--coeff-max', type=int, default=2,
                             help='Maximum coefficient value (default: 2)')
    brute_parser.add_argument('--strategy', 
                             choices=['lexicographic', 'degree_first'],
                             default='lexicographic',
                             help='Enumeration strategy (default: lexicographic)')
    brute_parser.add_argument('--checkpoint-interval', type=int, default=10,
                             help='Save state every N pairs (default: 10)')
    brute_parser.add_argument('--workers', type=int, default=4,
                             help='Number of parallel workers (default: 4)')
    brute_parser.add_argument('--resume', action='store_true',
                             help='Resume from last checkpoint')
    
    # Manual check mode
    manual_parser = subparsers.add_parser('check', 
                                         help='Check specific polynomial pair')
    manual_parser.add_argument('f', type=str, 
                              help='First polynomial (e.g., "x^2 + y^2")')
    manual_parser.add_argument('g', type=str,
                              help='Second polynomial (e.g., "x*y")')
    manual_parser.add_argument('--max-degree-q', type=int, default=3,
                              help='Maximum degree for dependency q (default: 3)')
    manual_parser.add_argument('--coeff-min', type=int, default=-2,
                              help='Minimum coefficient value (default: -2)')
    manual_parser.add_argument('--coeff-max', type=int, default=2,
                              help='Maximum coefficient value (default: 2)')
    
    # Statistics mode
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Query mode
    query_parser = subparsers.add_parser('query', help='Query results')
    query_parser.add_argument('--both-divisible', action='store_true',
                             help='Show only pairs where both conditions hold')
    query_parser.add_argument('--limit', type=int, default=20,
                             help='Maximum number of results to show (default: 20)')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.mode == 'brute':
            config = Config(
                max_degree_f=args.max_degree_f,
                max_degree_g=args.max_degree_g,
                max_degree_q=args.max_degree_q,
                coeff_min=args.coeff_min,
                coeff_max=args.coeff_max,
                enum_strategy=args.strategy,
                checkpoint_interval=args.checkpoint_interval,
                num_workers=args.workers
            )
            runner = BruteForceRunner(config)
            runner.run()
        
        elif args.mode == 'check':
            config = Config(
                max_degree_q=args.max_degree_q,
                coeff_min=args.coeff_min,
                coeff_max=args.coeff_max
            )
            checker = ManualChecker(config)
            checker.check_pair(args.f, args.g)
        
        elif args.mode == 'stats':
            cache = ResultCache('data/results.db')
            stats = cache.get_statistics()
            
            logger.info("="*100)
            logger.info("STATISTICS: ALL COMBINATIONS")
            logger.info("="*100)
            logger.info(f"\nTotal pairs checked: {stats['total']}")
            logger.info("")
            cursor = cache.conn.execute("""
                SELECT
                    CASE WHEN q_poly IS NULL THEN 0 ELSE 1 END as has_dep,
                    COALESCE(is_trivial, 0) as is_trivial,
                    COALESCE(df_divisible, 0) as df_div,
                    COALESCE(dg_divisible, 0) as dg_div,
                    COUNT(*) as count
                FROM results
                GROUP BY has_dep, is_trivial, df_div, dg_div
                ORDER BY has_dep DESC, is_trivial ASC, df_div DESC, dg_div DESC
            """)
            
            rows = cursor.fetchall()
            table_data = []
            for row in rows:
                has_dep, is_trivial, df_div, dg_div, count = row
                
                dep_status = "+" if has_dep else "-"
                trivial_status = "-" if is_trivial else "+" if has_dep else "-"
                df_status = "+" if df_div else "-"
                dg_status = "+" if dg_div else "-"
                both_status = "+" if (df_div and dg_div) else "-"
                pct = (count / stats['total'] * 100) if stats['total'] > 0 else 0
                
                table_data.append([
                    dep_status,
                    trivial_status,
                    df_status,
                    dg_status,
                    both_status,
                    count,
                    f"{pct:.2f}%"
                ])
            
            headers = [
                "Dependency\nFound",
                "Non-trivial\n(x^2/x*u/x*v)",
                "dq/df : dq/dx",
                "dq/dg : dq/dx",
                "Both\nDivisible",
                "Count",
                "Percent"
            ]
            
            logger.info(tabulate(table_data, headers=headers, tablefmt="grid"))
            
            logger.info("")
            logger.info("Legend:")
            logger.info("  + = Passed")
            logger.info("  - = Failed")
            logger.info("")
            logger.info("Note: Non-trivial means x appears as x^2 or x*u or x*v (not just linear like 4x-5)")
            
            cache.close()
        
        elif args.mode == 'query':
            cache = ResultCache('data/results.db')
            results = cache.query_results(both_divisible=args.both_divisible)
            
            logger.info("="*60)
            logger.info("QUERY RESULTS")
            logger.info("="*60)
            
            if args.both_divisible:
                logger.info("Showing pairs where both divisibility conditions hold")
            else:
                logger.info("Showing all results")
            
            logger.info(f"Limit: {args.limit}")
            logger.info("")
            
            if not results:
                logger.info("No results found.")
            else:
                for i, result in enumerate(results[:args.limit], 1):
                    logger.info(f"Result #{i}")
                    logger.info(f"  f = {result['f_poly']}")
                    logger.info(f"  g = {result['g_poly']}")
                    
                    if result['q_poly']:
                        logger.info(f"  q = {result['q_poly']}")
                        logger.info(f"  dq/du : dq/dx = {bool(result['df_divisible'])}")
                        logger.info(f"  dq/dv : dq/dx = {bool(result['dg_divisible'])}")
                    else:
                        logger.info(f"  No dependency found")
                    
                    logger.info(f"  Timestamp: {result['timestamp']}")
                    logger.info("")
                
                if len(results) > args.limit:
                    logger.info(f"... and {len(results) - args.limit} more results")
            
            cache.close()
    
    except KeyboardInterrupt:
        logger.info("\n\nInterrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

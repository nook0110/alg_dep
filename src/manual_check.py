"""Manual checker for specific polynomial pairs."""

from .config import Config
from .polynomial import parse_polynomial
from .dependency_finder import DependencyFinder
from .divisibility import DivisibilityChecker
from .cache import ResultCache


class ManualChecker:
    """Check specific polynomial pairs manually."""
    
    def __init__(self, config: Config):
        """
        Initialize manual checker.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.finder = DependencyFinder(config)
        self.checker = DivisibilityChecker()
        self.cache = ResultCache(config.cache_file)
    
    def check_pair(self, f_str: str, g_str: str):
        """
        Check specific polynomial pair.
        
        Args:
            f_str: First polynomial as string (e.g., "x^2 + y^2")
            g_str: Second polynomial as string
        """
        print("="*60)
        print("MANUAL CHECK")
        print("="*60)
        print(f"f = {f_str}")
        print(f"g = {g_str}")
        print()
        
        # Parse polynomials
        try:
            f = parse_polynomial(f_str)
            g = parse_polynomial(g_str)
        except Exception as e:
            print(f"Error parsing polynomials: {e}")
            return
        
        print(f"Parsed f = {f}")
        print(f"Parsed g = {g}")
        print()
        
        # Check cache
        cached = self.cache.get_result(f, g)
        if cached:
            print("Result found in cache:")
            self._print_result(cached)
            return
        
        # Find dependency
        print(f"Searching for dependency q(x, u, v) where q(x, f, g) = 0...")
        print(f"Max degree for q: {self.config.max_degree_q}")
        print()
        
        q = self.finder.find_dependency(f, g)
        
        if not q:
            print("No dependency found within degree bounds.")
            print()
            # Save negative result
            self.cache.save_result(f, g, None, {})
            return
        
        print(f"✓ Found dependency:")
        print(f"  q = {q}")
        print()
        
        # Check divisibility
        print("Checking divisibility conditions...")
        divisibility = self.checker.check_conditions(q, f, g)
        
        print(f"  ∂q/∂u : ∂q/∂x = {divisibility['df_divisible']}")
        print(f"  ∂q/∂v : ∂q/∂x = {divisibility['dg_divisible']}")
        print()
        
        if divisibility['both_divisible']:
            print("✓ Both divisibility conditions satisfied!")
        else:
            print("✗ Not all divisibility conditions satisfied.")
        
        print()
        
        # Save result
        self.cache.save_result(f, g, q, divisibility)
        print("Result saved to cache.")
    
    def _print_result(self, result: dict):
        """
        Print cached result.
        
        Args:
            result: Result dictionary from cache
        """
        print(f"  f = {result['f_poly']}")
        print(f"  g = {result['g_poly']}")
        
        if result['q_poly']:
            print(f"  q = {result['q_poly']}")
            print(f"  ∂q/∂u : ∂q/∂x = {bool(result['df_divisible'])}")
            print(f"  ∂q/∂v : ∂q/∂x = {bool(result['dg_divisible'])}")
            
            if result['both_divisible']:
                print("  ✓ Both conditions satisfied")
            else:
                print("  ✗ Not all conditions satisfied")
        else:
            print("  No dependency found")
        
        print(f"  Cached at: {result['timestamp']}")

import logging

from .config import Config
from .polynomial import parse_polynomial
from .dependency_finder import DependencyFinder
from .divisibility import DivisibilityChecker
from .cache import ResultCache

logger = logging.getLogger(__name__)


class ManualChecker:
    
    def __init__(self, config: Config):
        self.config = config
        self.finder = DependencyFinder(config)
        self.checker = DivisibilityChecker()
        self.cache = ResultCache(config.cache_file)
    
    def check_pair(self, f_str: str, g_str: str):
        logger.info("="*60)
        logger.info("MANUAL CHECK")
        logger.info("="*60)
        logger.info(f"f = {f_str}")
        logger.info(f"g = {g_str}")
        logger.info("")
        try:
            f = parse_polynomial(f_str)
            g = parse_polynomial(g_str)
        except Exception as e:
            logger.error(f"Error parsing polynomials: {e}")
            return
        
        logger.info(f"Parsed f = {f}")
        logger.info(f"Parsed g = {g}")
        logger.info("")
        cached = self.cache.get_result(f, g)
        if cached:
            logger.info("Result found in cache:")
            self._print_result(cached)
            return
        
        logger.info(f"Searching for dependency q(x, u, v) where q(x, f, g) = 0...")
        logger.info(f"Max degree for q: {self.config.max_degree_q}")
        logger.info("")
        
        q, was_trivial = self.finder.find_dependency(f, g)
        
        if not q:
            logger.info("No dependency found within degree bounds.")
            logger.info("")
            self.cache.save_result(f, g, None, {}, is_trivial=False)
            return
        
        if was_trivial:
            logger.info(f"- Found TRIVIAL dependency (only linear x):")
        else:
            logger.info(f"+ Found NON-TRIVIAL dependency:")
        logger.info(f"  q = {q}")
        logger.info("")
        
        logger.info("Checking divisibility conditions...")
        divisibility = self.checker.check_conditions(q, f, g)
        
        logger.info(f"  dq/du : dq/dx = {divisibility['df_divisible']}")
        logger.info(f"  dq/dv : dq/dx = {divisibility['dg_divisible']}")
        logger.info("")
        
        if divisibility['both_divisible']:
            logger.info("+ Both divisibility conditions satisfied!")
        else:
            logger.info("- Not all divisibility conditions satisfied.")
        
        logger.info("")
        
        self.cache.save_result(f, g, q, divisibility, is_trivial=was_trivial)
        logger.info("Result saved to cache.")
    
    def _print_result(self, result: dict):
        logger.info(f"  f = {result['f_poly']}")
        logger.info(f"  g = {result['g_poly']}")
        
        if result.get('is_trivial'):
            logger.info("  - Dependency found but rejected as trivial (only linear x)")
        elif result['q_poly']:
            logger.info(f"  q = {result['q_poly']}")
            logger.info(f"  dq/du : dq/dx = {bool(result['df_divisible'])}")
            logger.info(f"  dq/dv : dq/dx = {bool(result['dg_divisible'])}")
            
            if result['both_divisible']:
                logger.info("  + Both conditions satisfied")
            else:
                logger.info("  - Not all conditions satisfied")
        else:
            logger.info("  No dependency found")
        
        logger.info(f"  Cached at: {result['timestamp']}")

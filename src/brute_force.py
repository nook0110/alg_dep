from concurrent.futures import ProcessPoolExecutor, as_completed
from threading import Lock
import time
import logging

from .config import Config
from .generator import PolynomialGenerator
from .dependency_finder import DependencyFinder
from .divisibility import DivisibilityChecker
from .cache import ResultCache
from .state import BruteForceState

logger = logging.getLogger(__name__)


def process_pair_worker(args):
    f, g, config = args
    cache = ResultCache(config.cache_file)
    
    try:
        cached = cache.get_result(f, g)
        if cached:
            return (f, g, None, {}, False, True)
        finder = DependencyFinder(config)
        checker = DivisibilityChecker()
        q, was_trivial = finder.find_dependency(f, g)
        divisibility = {}
        if q:
            divisibility = checker.check_conditions(q, f, g)
        
        return (f, g, q, divisibility, was_trivial, False)
    finally:
        cache.close()


class BruteForceRunner:
    
    def __init__(self, config: Config):
        self.config = config
        self.generator = PolynomialGenerator(config)
        self.state = BruteForceState.load(config.state_file)
        self.state_lock = Lock()
        self.cache_lock = Lock()
        self.checkpoint_counter = 0
    
    def run(self):
        logger.info("Starting brute force search...")
        logger.info(f"Configuration:")
        logger.info(f"  Max degree f: {self.config.max_degree_f}")
        logger.info(f"  Max degree g: {self.config.max_degree_g}")
        logger.info(f"  Max degree q: {self.config.max_degree_q}")
        logger.info(f"  Coefficient range: [{self.config.coeff_min}, {self.config.coeff_max}]")
        logger.info(f"  Strategy: {self.config.enum_strategy}")
        logger.info(f"  Workers: {self.config.num_workers}")
        
        if self.state.total_pairs_checked > 0:
            logger.info("Resuming from previous state:")
            logger.info(self.state.get_summary())
        
        try:
            pairs_batch = []
            
            for f, g in self.generator.generate_pairs():
                pairs_batch.append((f, g))
                if len(pairs_batch) >= self.config.batch_size:
                    self._process_batch(pairs_batch)
                    pairs_batch = []
            if pairs_batch:
                self._process_batch(pairs_batch)
        
        except KeyboardInterrupt:
            logger.info("Interrupted by user. Saving state...")
            self.state.save(self.config.state_file)
            logger.info("State saved. You can resume later with --resume flag.")
        
        finally:
            self.state.save(self.config.state_file)
            
            logger.info("="*60)
            logger.info("FINAL STATISTICS")
            logger.info("="*60)
            logger.info(self.state.get_summary())
            cache = ResultCache(self.config.cache_file)
            try:
                stats = cache.get_statistics()
                logger.info("Detailed Statistics:")
                logger.info(f"  Total pairs checked: {stats['total']}")
                logger.info(f"  Dependencies found: {stats['with_dependency']}")
                logger.info(f"    - Trivial (rejected): {stats['trivial_rejected']}")
                logger.info(f"    - Non-trivial (kept): {stats['nontrivial_found']}")
                logger.info(f"  No dependency found: {stats['no_dependency']}")
                logger.info("Divisibility Results (for non-trivial dependencies):")
                logger.info(f"  dq/df : dq/dx only: {stats['df_divisible_only']}")
                logger.info(f"  dq/dg : dq/dx only: {stats['dg_divisible_only']}")
                logger.info(f"  Both conditions satisfied: {stats['both_divisible']}")
            finally:
                cache.close()
    
    def _process_batch(self, pairs_batch):
        cache = ResultCache(self.config.cache_file)
        cached_pairs = []
        non_cached_pairs = []
        
        try:
            for f, g in pairs_batch:
                if cache.get_result(f, g):
                    cached_pairs.append((f, g))
                else:
                    non_cached_pairs.append((f, g))
        finally:
            cache.close()
        
        for f, g in cached_pairs:
            logger.info(f"[CACHED] f={f}, g={g}")
        
        if not non_cached_pairs:
            return
        
        worker_args = [(f, g, self.config) for f, g in non_cached_pairs]
        
        with ProcessPoolExecutor(max_workers=self.config.num_workers) as executor:
            future_to_pair = {
                executor.submit(process_pair_worker, args): args[:2]
                for args in worker_args
            }
            for future in as_completed(future_to_pair):
                f, g = future_to_pair[future]
                
                try:
                    f_result, g_result, q, divisibility, was_trivial, was_cached = future.result()
                    
                    logger.info(f"[CHECKED] f={f}, g={g}")
                    
                    if q:
                        if was_trivial:
                            logger.info(f"  Found TRIVIAL dependency (only linear x): q={q}")
                        else:
                            logger.info(f"  Found NON-TRIVIAL dependency: q={q}")
                        logger.info(f"  dq/df : dq/dx = {divisibility['df_divisible']}")
                        logger.info(f"  dq/dg : dq/dx = {divisibility['dg_divisible']}")
                    else:
                        logger.info(f"  No dependency found")
                    with self.cache_lock:
                        cache = ResultCache(self.config.cache_file)
                        try:
                            cache.save_result(f, g, q, divisibility, was_trivial)
                        finally:
                            cache.close()
                    
                    with self.state_lock:
                        self.state.update_progress(0, 0, q is not None)
                        self.checkpoint_counter += 1
                        
                        if self.checkpoint_counter >= self.config.checkpoint_interval:
                            self.state.save(self.config.state_file)
                            self.checkpoint_counter = 0
                            logger.info(f"[CHECKPOINT] {self.state.total_pairs_checked} pairs checked")
                
                except Exception as e:
                    logger.error(f"[ERROR] Failed to process f={f}, g={g}: {e}")
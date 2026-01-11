"""Brute force runner with checkpointing."""

from .config import Config
from .generator import PolynomialGenerator
from .dependency_finder import DependencyFinder
from .divisibility import DivisibilityChecker
from .cache import ResultCache
from .state import BruteForceState


class BruteForceRunner:
    """Run brute force search with state persistence."""
    
    def __init__(self, config: Config):
        """
        Initialize brute force runner.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.generator = PolynomialGenerator(config)
        self.finder = DependencyFinder(config)
        self.checker = DivisibilityChecker()
        self.cache = ResultCache(config.cache_file)
        self.state = BruteForceState.load(config.state_file)
    
    def run(self):
        """Run brute force search with checkpointing."""
        print("Starting brute force search...")
        print(f"Configuration:")
        print(f"  Max degree f: {self.config.max_degree_f}")
        print(f"  Max degree g: {self.config.max_degree_g}")
        print(f"  Max degree q: {self.config.max_degree_q}")
        print(f"  Coefficient range: [{self.config.coeff_min}, {self.config.coeff_max}]")
        print(f"  Strategy: {self.config.enum_strategy}")
        print()
        
        if self.state.total_pairs_checked > 0:
            print("Resuming from previous state:")
            print(self.state.get_summary())
            print()
        
        checkpoint_counter = 0
        
        try:
            for f, g in self.generator.generate_pairs():
                # Check cache first
                cached = self.cache.get_result(f, g)
                if cached:
                    print(f"[CACHED] f={f}, g={g}")
                    continue
                
                print(f"[CHECKING] f={f}, g={g}")
                
                # Find dependency
                q = self.finder.find_dependency(f, g)
                
                # Check divisibility if dependency found
                divisibility = {}
                if q:
                    divisibility = self.checker.check_conditions(q, f, g)
                    print(f"  Found q={q}")
                    print(f"  ∂q/∂f : ∂q/∂x = {divisibility['df_divisible']}")
                    print(f"  ∂q/∂g : ∂q/∂x = {divisibility['dg_divisible']}")
                else:
                    print(f"  No dependency found")
                
                # Save result
                self.cache.save_result(f, g, q, divisibility)
                
                # Update state
                self.state.update_progress(0, 0, q is not None)
                
                # Checkpoint
                checkpoint_counter += 1
                if checkpoint_counter >= self.config.checkpoint_interval:
                    self.state.save(self.config.state_file)
                    checkpoint_counter = 0
                    print(f"[CHECKPOINT] {self.state.total_pairs_checked} pairs checked")
                    print()
        
        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Saving state...")
            self.state.save(self.config.state_file)
            print("State saved. You can resume later with --resume flag.")
        
        finally:
            # Final save
            self.state.save(self.config.state_file)
            
            # Print final statistics
            print("\n" + "="*60)
            print("FINAL STATISTICS")
            print("="*60)
            print(self.state.get_summary())
            
            stats = self.cache.get_statistics()
            print(f"\nCache statistics:")
            print(f"  Total results: {stats['total']}")
            print(f"  With dependency: {stats['with_dependency']}")
            print(f"  Both conditions satisfied: {stats['both_divisible']}")
            
            self.cache.close()
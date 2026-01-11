"""Configuration management for polynomial dependency checker."""

from dataclasses import dataclass
from typing import Literal


@dataclass
class Config:
    """Configuration for polynomial dependency checker."""
    
    # Polynomial generation
    max_degree_f: int = 2
    max_degree_g: int = 2
    max_degree_q: int = 3
    coeff_min: int = -2
    coeff_max: int = 2
    
    # Enumeration strategy
    enum_strategy: Literal["lexicographic", "degree_first"] = "lexicographic"
    skip_trivial: bool = True  # Skip constant polynomials
    
    # Storage
    cache_file: str = "data/results.db"
    state_file: str = "data/state.json"
    
    # Performance
    batch_size: int = 100
    checkpoint_interval: int = 10  # Save state every N pairs
    
    def __post_init__(self):
        """Validate configuration."""
        if self.max_degree_f < 0 or self.max_degree_g < 0 or self.max_degree_q < 0:
            raise ValueError("Degrees must be non-negative")
        if self.coeff_min > self.coeff_max:
            raise ValueError("coeff_min must be <= coeff_max")
        if self.checkpoint_interval < 1:
            raise ValueError("checkpoint_interval must be >= 1")

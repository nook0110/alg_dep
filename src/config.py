from dataclasses import dataclass
from typing import Literal


@dataclass
class Config:
    
    max_degree_f: int = 2
    max_degree_g: int = 2
    max_degree_q: int = 3
    coeff_min: int = -2
    coeff_max: int = 2
    enum_strategy: Literal["lexicographic", "degree_first"] = "lexicographic"
    skip_trivial: bool = True
    cache_file: str = "data/results.db"
    state_file: str = "data/state.json"
    batch_size: int = 100
    checkpoint_interval: int = 10
    num_workers: int = 4
    
    def __post_init__(self):
        if self.max_degree_f < 0 or self.max_degree_g < 0 or self.max_degree_q < 0:
            raise ValueError("Degrees must be non-negative")
        if self.coeff_min > self.coeff_max:
            raise ValueError("coeff_min must be <= coeff_max")
        if self.checkpoint_interval < 1:
            raise ValueError("checkpoint_interval must be >= 1")

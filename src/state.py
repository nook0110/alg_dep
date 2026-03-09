import json
import os
from datetime import datetime
from typing import Optional


class BruteForceState:
    
    def __init__(self):
        self.last_f_index: int = 0
        self.last_g_index: int = 0
        self.total_pairs_checked: int = 0
        self.pairs_with_dependency: int = 0
        self.start_time: Optional[str] = None
        self.last_checkpoint: Optional[str] = None
    
    def save(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        self.last_checkpoint = datetime.now().isoformat()
        with open(filepath, 'w') as f:
            json.dump({
                'last_f_index': self.last_f_index,
                'last_g_index': self.last_g_index,
                'total_pairs_checked': self.total_pairs_checked,
                'pairs_with_dependency': self.pairs_with_dependency,
                'start_time': self.start_time,
                'last_checkpoint': self.last_checkpoint
            }, f, indent=2)
    
    @classmethod
    def load(cls, filepath: str) -> 'BruteForceState':
        state = cls()
        
        if not os.path.exists(filepath):
            state.start_time = datetime.now().isoformat()
            return state
        
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                state.last_f_index = data.get('last_f_index', 0)
                state.last_g_index = data.get('last_g_index', 0)
                state.total_pairs_checked = data.get('total_pairs_checked', 0)
                state.pairs_with_dependency = data.get('pairs_with_dependency', 0)
                state.start_time = data.get('start_time')
                state.last_checkpoint = data.get('last_checkpoint')
        except (json.JSONDecodeError, IOError):
            state.start_time = datetime.now().isoformat()
        
        return state
    
    def update_progress(self, f_index: int, g_index: int, found_dependency: bool):
        self.last_f_index = f_index
        self.last_g_index = g_index
        self.total_pairs_checked += 1
        if found_dependency:
            self.pairs_with_dependency += 1
    
    def get_summary(self) -> str:
        lines = [
            f"Total pairs checked: {self.total_pairs_checked}",
            f"Pairs with dependency: {self.pairs_with_dependency}",
            f"Last position: f_index={self.last_f_index}, g_index={self.last_g_index}",
        ]
        
        if self.start_time:
            lines.append(f"Started: {self.start_time}")
        if self.last_checkpoint:
            lines.append(f"Last checkpoint: {self.last_checkpoint}")
        
        return "\n".join(lines)
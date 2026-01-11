"""State persistence for brute force progress."""

import json
import os
from datetime import datetime
from typing import Optional


class BruteForceState:
    """Track and persist brute force enumeration progress."""
    
    def __init__(self):
        """Initialize empty state."""
        self.last_f_index: int = 0
        self.last_g_index: int = 0
        self.total_pairs_checked: int = 0
        self.pairs_with_dependency: int = 0
        self.start_time: Optional[str] = None
        self.last_checkpoint: Optional[str] = None
    
    def save(self, filepath: str):
        """
        Save state to JSON file.
        
        Args:
            filepath: Path to save state file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Update checkpoint time
        self.last_checkpoint = datetime.now().isoformat()
        
        # Save to JSON
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
        """
        Load state from JSON file.
        
        Args:
            filepath: Path to state file
            
        Returns:
            BruteForceState object
        """
        state = cls()
        
        if not os.path.exists(filepath):
            # Initialize start time for new state
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
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load state from {filepath}: {e}")
            print("Starting with fresh state")
            state.start_time = datetime.now().isoformat()
        
        return state
    
    def update_progress(self, f_index: int, g_index: int, found_dependency: bool):
        """
        Update progress counters.
        
        Args:
            f_index: Current f polynomial index
            g_index: Current g polynomial index
            found_dependency: Whether a dependency was found
        """
        self.last_f_index = f_index
        self.last_g_index = g_index
        self.total_pairs_checked += 1
        if found_dependency:
            self.pairs_with_dependency += 1
    
    def get_summary(self) -> str:
        """
        Get human-readable summary of state.
        
        Returns:
            Summary string
        """
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
"""Result caching with SQLite database."""

import sqlite3
import os
from typing import Optional, Dict, List

from .polynomial import poly_hash


class ResultCache:
    """Cache results for polynomial pairs using SQLite."""
    
    def __init__(self, db_path: str):
        """
        Initialize result cache.
        
        Args:
            db_path: Path to SQLite database file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                f_poly TEXT NOT NULL,
                g_poly TEXT NOT NULL,
                f_hash TEXT NOT NULL,
                g_hash TEXT NOT NULL,
                q_poly TEXT,
                df_divisible INTEGER,
                dg_divisible INTEGER,
                both_divisible INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(f_hash, g_hash)
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_hashes 
            ON results(f_hash, g_hash)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_both_divisible 
            ON results(both_divisible)
        """)
        
        self.conn.commit()
    
    def get_result(self, f, g) -> Optional[Dict]:
        """
        Check if result exists for this polynomial pair.
        
        Args:
            f: First polynomial (SymPy expression)
            g: Second polynomial (SymPy expression)
            
        Returns:
            Dictionary with result data if found, None otherwise
        """
        f_hash_val = poly_hash(f)
        g_hash_val = poly_hash(g)
        
        cursor = self.conn.execute(
            "SELECT * FROM results WHERE f_hash = ? AND g_hash = ?",
            (f_hash_val, g_hash_val)
        )
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def save_result(self, f, g, q: Optional, divisibility: Dict[str, bool]):
        """
        Save result for polynomial pair.
        
        Args:
            f: First polynomial (SymPy expression)
            g: Second polynomial (SymPy expression)
            q: Dependency polynomial (SymPy expression) or None
            divisibility: Dictionary with divisibility results
        """
        f_str = str(f)
        g_str = str(g)
        f_hash_val = poly_hash(f)
        g_hash_val = poly_hash(g)
        q_str = str(q) if q is not None else None
        
        self.conn.execute("""
            INSERT OR REPLACE INTO results 
            (f_poly, g_poly, f_hash, g_hash, q_poly, df_divisible, dg_divisible, both_divisible)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            f_str, g_str,
            f_hash_val, g_hash_val,
            q_str,
            1 if divisibility.get('df_divisible') else 0,
            1 if divisibility.get('dg_divisible') else 0,
            1 if divisibility.get('both_divisible') else 0
        ))
        
        self.conn.commit()
    
    def get_statistics(self) -> Dict:
        """
        Get summary statistics.
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN q_poly IS NOT NULL THEN 1 ELSE 0 END) as with_dependency,
                SUM(CASE WHEN both_divisible = 1 THEN 1 ELSE 0 END) as both_divisible
            FROM results
        """)
        
        row = cursor.fetchone()
        return {
            'total': row['total'],
            'with_dependency': row['with_dependency'] or 0,
            'both_divisible': row['both_divisible'] or 0
        }
    
    def query_results(self, both_divisible: bool = False) -> List[Dict]:
        """
        Query results from database.
        
        Args:
            both_divisible: If True, only return results where both conditions hold
            
        Returns:
            List of result dictionaries
        """
        if both_divisible:
            cursor = self.conn.execute("""
                SELECT * FROM results 
                WHERE both_divisible = 1
                ORDER BY timestamp DESC
            """)
        else:
            cursor = self.conn.execute("""
                SELECT * FROM results 
                ORDER BY timestamp DESC
            """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
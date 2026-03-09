from itertools import product
from typing import Iterator, Tuple
from sympy import symbols
from sympy.abc import x, y

from .config import Config


class PolynomialGenerator:
    
    def __init__(self, config: Config):
        self.config = config
        self.x, self.y = x, y
    
    def generate_pairs(self) -> Iterator[Tuple]:
        if self.config.enum_strategy == "lexicographic":
            yield from self._generate_lexicographic()
        elif self.config.enum_strategy == "degree_first":
            yield from self._generate_degree_first()
        else:
            raise ValueError(f"Unknown strategy: {self.config.enum_strategy}")
    
    def _generate_lexicographic(self) -> Iterator[Tuple]:
        for f in self._generate_polynomials(self.config.max_degree_f):
            for g in self._generate_polynomials(self.config.max_degree_g):
                if self._should_skip(f, g):
                    continue
                yield (f, g)
    
    def _generate_degree_first(self) -> Iterator[Tuple]:
        for deg_f in range(self.config.max_degree_f + 1):
            for deg_g in range(self.config.max_degree_g + 1):
                for f in self._generate_polynomials_of_degree(deg_f):
                    for g in self._generate_polynomials_of_degree(deg_g):
                        if self._should_skip(f, g):
                            continue
                        yield (f, g)
    
    def _generate_polynomials(self, max_degree: int) -> Iterator:
        monomials = []
        for deg in range(max_degree + 1):
            for i in range(deg + 1):
                j = deg - i
                monomials.append((i, j))
        coeff_range = range(self.config.coeff_min, self.config.coeff_max + 1)
        
        for coeffs in product(coeff_range, repeat=len(monomials)):
            poly = sum(c * (self.x**i) * (self.y**j) 
                      for c, (i, j) in zip(coeffs, monomials))
            if poly == 0 and self.config.skip_trivial:
                continue
            
            yield poly
    
    def _generate_polynomials_of_degree(self, degree: int) -> Iterator:
        monomials = []
        for i in range(degree + 1):
            j = degree - i
            monomials.append((i, j))  # x^i * y^j
        
        # Also include lower degree terms
        for lower_deg in range(degree):
            for i in range(lower_deg + 1):
                j = lower_deg - i
                monomials.append((i, j))
        
        coeff_range = range(self.config.coeff_min, self.config.coeff_max + 1)
        
        for coeffs in product(coeff_range, repeat=len(monomials)):
            # Ensure at least one coefficient of highest degree is non-zero
            highest_deg_coeffs = coeffs[:degree + 1]
            if all(c == 0 for c in highest_deg_coeffs):
                continue
            
            poly = sum(c * (self.x**i) * (self.y**j) 
                      for c, (i, j) in zip(coeffs, monomials))
            
            if poly == 0 and self.config.skip_trivial:
                continue
            
            yield poly
    
    def count_total_pairs(self) -> int:
        """
        Count total number of polynomial pairs to be generated.
        
        Returns:
            Total number of pairs
        """
        num_coeffs_f = sum(deg + 1 for deg in range(self.config.max_degree_f + 1))
        num_coeffs_g = sum(deg + 1 for deg in range(self.config.max_degree_g + 1))
        
        coeff_range_size = self.config.coeff_max - self.config.coeff_min + 1
        
        total_f = coeff_range_size ** num_coeffs_f
        total_g = coeff_range_size ** num_coeffs_g
        
        return total_f * total_g
    
    def _should_skip(self, f, g) -> bool:
        """
        Check if polynomial pair should be skipped.
        
        Args:
            f: First polynomial
            g: Second polynomial
            
        Returns:
            True if should skip, False otherwise
        """
        if self.config.skip_trivial:
            # Skip if both are constants
            if f.is_number and g.is_number:
                return True
            # Skip if both are zero
            if f == 0 and g == 0:
                return True
        
        return False

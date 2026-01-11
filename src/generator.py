"""Polynomial generator for brute force enumeration."""

from itertools import product
from typing import Iterator, Tuple
from sympy import symbols
from sympy.abc import x, y

from .config import Config


class PolynomialGenerator:
    """Generate polynomial pairs for brute force search."""
    
    def __init__(self, config: Config):
        """
        Initialize generator with configuration.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.x, self.y = x, y
    
    def generate_pairs(self) -> Iterator[Tuple]:
        """
        Generate (f, g) polynomial pairs according to strategy.
        
        Yields:
            Tuples of (f, g) where f and g are SymPy expressions
        """
        if self.config.enum_strategy == "lexicographic":
            yield from self._generate_lexicographic()
        elif self.config.enum_strategy == "degree_first":
            yield from self._generate_degree_first()
        else:
            raise ValueError(f"Unknown strategy: {self.config.enum_strategy}")
    
    def _generate_lexicographic(self) -> Iterator[Tuple]:
        """Generate polynomials in lexicographic order of coefficients."""
        for f in self._generate_polynomials(self.config.max_degree_f):
            for g in self._generate_polynomials(self.config.max_degree_g):
                if self._should_skip(f, g):
                    continue
                yield (f, g)
    
    def _generate_degree_first(self) -> Iterator[Tuple]:
        """Generate polynomials degree by degree."""
        for deg_f in range(self.config.max_degree_f + 1):
            for deg_g in range(self.config.max_degree_g + 1):
                for f in self._generate_polynomials_of_degree(deg_f):
                    for g in self._generate_polynomials_of_degree(deg_g):
                        if self._should_skip(f, g):
                            continue
                        yield (f, g)
    
    def _generate_polynomials(self, max_degree: int) -> Iterator:
        """
        Generate all polynomials up to max_degree.
        
        Args:
            max_degree: Maximum total degree
            
        Yields:
            SymPy polynomial expressions
        """
        # Generate all monomials up to max_degree
        monomials = []
        for deg in range(max_degree + 1):
            for i in range(deg + 1):
                j = deg - i
                monomials.append((i, j))  # x^i * y^j
        
        # Generate all coefficient combinations
        coeff_range = range(self.config.coeff_min, self.config.coeff_max + 1)
        
        for coeffs in product(coeff_range, repeat=len(monomials)):
            # Build polynomial
            poly = sum(c * (self.x**i) * (self.y**j) 
                      for c, (i, j) in zip(coeffs, monomials))
            
            # Skip if all coefficients are zero
            if poly == 0 and self.config.skip_trivial:
                continue
            
            yield poly
    
    def _generate_polynomials_of_degree(self, degree: int) -> Iterator:
        """
        Generate all polynomials of exact degree.
        
        Args:
            degree: Exact degree
            
        Yields:
            SymPy polynomial expressions
        """
        # Generate monomials of exact degree
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
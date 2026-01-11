"""Polynomial operations using SymPy."""

from sympy import symbols, sympify, div, simplify, expand
from sympy.abc import x, y, u, v


def parse_polynomial(expr: str):
    """
    Parse polynomial string into SymPy expression.
    
    Supports format: x^2 + y^2 - 1
    Converts ^ to ** for SymPy compatibility.
    
    Args:
        expr: Polynomial string
        
    Returns:
        SymPy expression
    """
    # Replace ^ with ** for SymPy
    expr = expr.replace('^', '**')
    return sympify(expr)


def partial_derivative(poly, var):
    """
    Compute partial derivative ∂poly/∂var.
    
    Args:
        poly: SymPy expression
        var: Variable symbol (x, y, u, or v)
        
    Returns:
        SymPy expression of derivative
    """
    return poly.diff(var)


def substitute(poly, var, expr):
    """
    Substitute variable with expression.
    
    Args:
        poly: SymPy expression
        var: Variable to substitute
        expr: Expression to substitute with
        
    Returns:
        SymPy expression after substitution
    """
    result = poly.subs(var, expr)
    return expand(simplify(result))


def is_divisible(dividend, divisor):
    """
    Check if dividend is divisible by divisor.
    
    Args:
        dividend: SymPy expression
        divisor: SymPy expression
        
    Returns:
        True if divisible (remainder is 0), False otherwise
    """
    if divisor == 0:
        return False
    
    _, remainder = div(dividend, divisor, domain='QQ')
    return remainder == 0


def poly_hash(poly):
    """
    Generate hash for polynomial (for caching).
    
    Args:
        poly: SymPy expression
        
    Returns:
        Hash string
    """
    return str(expand(poly))


def is_zero(poly):
    """
    Check if polynomial is identically zero.
    
    Args:
        poly: SymPy expression
        
    Returns:
        True if zero, False otherwise
    """
    return simplify(expand(poly)) == 0


def total_degree(poly):
    """
    Get total degree of polynomial.
    
    Args:
        poly: SymPy expression
        
    Returns:
        Total degree as integer
    """
    from sympy import degree as sympy_degree
    from sympy import Poly as SymPyPoly
    
    try:
        # Try to convert to Poly object
        p = SymPyPoly(poly)
        return p.total_degree()
    except:
        # Fallback: return 0 for constants
        if poly.is_number:
            return 0
        # For more complex expressions, estimate degree
        return 0
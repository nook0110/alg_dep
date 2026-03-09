from sympy import sympify, expand
from sympy.abc import x, y, u, v


def parse_polynomial(expr: str):
    expr = expr.replace('^', '**')
    return sympify(expr)


def partial_derivative(poly, var):
    return poly.diff(var)


def substitute(poly, var, expr):
    return poly.subs(var, expr)


def is_divisible(dividend, divisor):
    if divisor == 0:
        return False
    
    try:
        from sympy import rem
        
        if dividend == 0:
            return True
            
        remainder = rem(dividend, divisor)
        return remainder == 0
    except:
        return False


def poly_hash(poly):
    return str(expand(poly))


def is_zero(poly):
    return simplify(expand(poly)) == 0


def total_degree(poly):
    from sympy import degree as sympy_degree
    from sympy import Poly as SymPyPoly
    
    try:
        p = SymPyPoly(poly)
        return p.total_degree()
    except:
        if poly.is_number:
            return 0
        return 0
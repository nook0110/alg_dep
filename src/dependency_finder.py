from typing import Optional
from sympy import Poly
from sympy.abc import x, y, u, v

from .config import Config


class DependencyFinder:
    
    def __init__(self, config: Config):
        self.config = config
        self.x, self.y, self.u, self.v = x, y, u, v
    
    def _is_nontrivial_in_x(self, q) -> bool:
        from sympy import degree, Poly
        
        try:
            poly = Poly(q, self.x, self.u, self.v)
            
            for monom, coeff in poly.terms():
                x_deg, u_deg, v_deg = monom
                if x_deg == 0:
                    continue
                if x_deg >= 2:
                    return True
                if x_deg == 1:
                    if u_deg > 0 or v_deg > 0:
                        return True
            return False
            
        except:
            return True
    
    def find_dependency(self, f, g):
        q = self._try_resultant(f, g)
        if q is not None:
            is_trivial = not self._is_nontrivial_in_x(q)
            return q, is_trivial
        
        # No dependency found
        return None, False
    
    def _try_resultant(self, f, g) -> Optional:
        """
        Use resultant to find dependency by eliminating y.
        
        Given f(x,y) and g(x,y), we want to find q(x,u,v) such that
        q(x, f(x,y), g(x,y)) = 0.
        
        Method:
        - Consider p1 = u - f(x,y) and p2 = v - g(x,y)
        - Compute resultant Res_y(p1, p2) to eliminate y
        - This gives a polynomial in x, u, v
        
        Args:
            f: First polynomial
            g: Second polynomial
            
        Returns:
            Dependency found via resultant, or None
        """
        try:
            from sympy import Poly
            
            # Create polynomials u - f(x,y) and v - g(x,y)
            p1 = self.u - f
            p2 = self.v - g
            
            # Convert to Poly objects for faster resultant
            poly1 = Poly(p1, self.y, domain='ZZ[x,u,v]')
            poly2 = Poly(p2, self.y, domain='ZZ[x,u,v]')
            
            # Compute resultant with respect to y
            res = poly1.resultant(poly2)
            
            # Convert back to expression
            res = res.as_expr()
            
            # Check if it's non-trivial and valid
            if res != 0 and self.y not in res.free_symbols:
                # Quick verification without expensive is_dependency check
                return res
            
            return None
        except Exception:
            return None
    
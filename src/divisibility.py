"""Check divisibility conditions for algebraic dependencies."""

from typing import Dict
from sympy.abc import x, u, v

from .polynomial import partial_derivative, is_divisible, substitute


class DivisibilityChecker:
    """Check if ∂q/∂f : ∂q/∂x and ∂q/∂g : ∂q/∂x."""
    
    def __init__(self):
        """Initialize divisibility checker."""
        self.x, self.u, self.v = x, u, v
    
    def check_conditions(self, q, f, g) -> Dict[str, bool]:
        """
        Check divisibility conditions for dependency polynomial q.
        
        Given q(x, u, v) where u represents f and v represents g:
        1. Compute ∂q/∂x, ∂q/∂u, ∂q/∂v
        2. Substitute u → f(x,y), v → g(x,y) in the derivatives
        3. Check if ∂q/∂u|_{u=f,v=g} is divisible by ∂q/∂x|_{u=f,v=g}
        4. Check if ∂q/∂v|_{u=f,v=g} is divisible by ∂q/∂x|_{u=f,v=g}
        
        Args:
            q: Dependency polynomial in Q[x,u,v]
            f: First polynomial in Z[x,y]
            g: Second polynomial in Z[x,y]
            
        Returns:
            Dictionary with keys:
                - 'df_divisible': bool (∂q/∂u : ∂q/∂x after substitution)
                - 'dg_divisible': bool (∂q/∂v : ∂q/∂x after substitution)
                - 'both_divisible': bool (both conditions hold)
        """
        # Compute partial derivatives of q
        dq_dx = partial_derivative(q, self.x)
        dq_du = partial_derivative(q, self.u)
        dq_dv = partial_derivative(q, self.v)

        # Substitute u → f(x,y), v → g(x,y) in all derivatives
        dq_dx_sub = substitute(substitute(dq_dx, self.u, f), self.v, g)
        dq_du_sub = substitute(substitute(dq_du, self.u, f), self.v, g)
        dq_dv_sub = substitute(substitute(dq_dv, self.u, f), self.v, g)

        # Check divisibility after substitution
        df_divisible = is_divisible(dq_du_sub, dq_dx_sub)
        dg_divisible = is_divisible(dq_dv_sub, dq_dx_sub)

        
        return {
            'df_divisible': df_divisible,
            'dg_divisible': dg_divisible,
            'both_divisible': df_divisible and dg_divisible
        }
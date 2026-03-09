from typing import Dict
from sympy.abc import x, u, v

from .polynomial import partial_derivative, is_divisible, substitute


class DivisibilityChecker:
    
    def __init__(self):
        self.x, self.u, self.v = x, u, v
    
    def check_conditions(self, q, f, g) -> Dict[str, bool]:
        try:
            dq_dx = q.diff(self.x)
            dq_du = q.diff(self.u)
            dq_dv = q.diff(self.v)
            dq_dx_sub = dq_dx.subs([(self.u, f), (self.v, g)])
            dq_du_sub = dq_du.subs([(self.u, f), (self.v, g)])
            dq_dv_sub = dq_dv.subs([(self.u, f), (self.v, g)])
            df_divisible = is_divisible(dq_du_sub, dq_dx_sub)
            dg_divisible = is_divisible(dq_dv_sub, dq_dx_sub)

            return {
                'df_divisible': df_divisible,
                'dg_divisible': dg_divisible,
                'both_divisible': df_divisible and dg_divisible
            }
        except Exception:
            return {
                'df_divisible': False,
                'dg_divisible': False,
                'both_divisible': False
            }
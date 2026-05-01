from typing import Callable, Any, Dict
from functools import wraps
from .curation_policy import CurationPolicy, VaultState, CurationParams

def with_curation_guard(
    params: CurationParams,
    risk_model: RiskModel,
    policy: CurationPolicy,
):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            state = args[0] if args else kwargs.get("state", None)
            if state is None:
                return {"status": "error", "reason": "no_state"}

            risk_profile = risk_model.get_vault_risk_profile(state)
            if risk_profile["max_risk"] > params.risk_score_cap:
                return {"status": "skipped_risk", "reason": "max_risk_threshold_violated"}

            errors = policy.check_vault(state, params)
            if errors:
                return {"status": "unsafe", "reason": "; ".join(errors.keys()), "errors": errors}

            reb_status = policy.check_rebalance(state, params, risk_model)
            if "unsafe" in reb_status["status"]:
                return reb_status

            return func(*args, **kwargs)
        return wrapper
    return decorator

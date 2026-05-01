from typing import Dict, Any, List
from dataclasses import dataclass
from .core.vault_ops import VaultState
from .core.risk_model import RiskModel, ProtocolRisk

@dataclass
class CurationPolicy:
    params: CurationParams

    def check_vault(self, state: VaultState, params: CurationParams) -> Dict[str, str]:
        errors = {}

        # 1. Lido‑style buffer
        if state.staked_eth > (1.0 - params.unpooled_eth_ratio) * state.deposited_eth:
            errors["buffer_violation"] = "too much ETH deployed"

        # 2. LTV cap
        if state.ltvl > params.max_ltv:
            errors["ltv_cap"] = f"LTV {state.ltvl} > max {params.max_ltv}"

        # 3. Health‑factor floor
        if state.health_factor < params.min_health_factor:
            errors["hf_floor"] = "HF too low"

        # 4. Loop‑factor cap
        if state.loop_factor > params.max_loop_factor:
            errors["loop_factor"] = "loop factor too high"

        # 5. Max per‑protocol exposure
        total_exposure = sum(state.protocols.values()) if state.protocols else 0.0
        if state.protocols:
            for p, a in state.protocols.items():
                if a / total_exposure > params.max_exposure_per_protocol:
                    errors[f"exposure_cap_{p}"] = f"Too much in {p}"

        # 6. AVS / restaking exposure cap
        avs_exposure = sum(a for p, a in state.protocols.items() if "AVS" in p.upper())
        total_exposure = sum(state.protocols.values()) if state.protocols else 0.0
        if total_exposure > 0 and avs_exposure / total_exposure > params.max_restaking_avs_exposure:
            errors["avs_cap"] = "AVS exposure too high"

        return errors

    def check_rebalance(self, state: VaultState, params: CurationParams, risk_model: RiskModel) -> Dict[str, str]:
        # 1. Emergency‑level HF
        if state.health_factor < params.emergency_redline_hf:
            return {"status": "unsafe_emergency", "reason": "emergency HF breach"}

        risk_profile = risk_model.get_vault_risk_profile(state)
        # 2. Risk‑score cap
        if risk_profile["max_risk"] > params.risk_score_cap:
            return {"status": "unsafe_risk", "reason": "max risk score breach"}

        # 3. Rebalance‑trigger based on LTV near cap
        if abs(state.ltvl - params.max_ltv) < 1e-3:
            return {"status": "need_rebalance", "reason": "near LTV cap"}

        return {"status": "safe"}

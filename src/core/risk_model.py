from typing import Dict, List
from dataclasses import dataclass

@dataclass
class ProtocolRisk:
    protocol: str
    volatility: float
    drawdown_90d: float
    audit_score: float
    tvl: float
    oracle_score: float
    exp_score: float

    def compute_risk_score(self, weights: Dict[str, float]) -> float:
        w = weights
        score = (
            w["volatility"] * self.volatility +
            w["drawdown"] * self.drawdown_90d +
            w["audit"] * (1.0 - self.audit_score) +
            w["exp"] * (1.0 - self.exp_score) +
            w["oracle"] * (1.0 - self.oracle_score)
        )
        return min(1.0, max(0.0, score))

class RiskModel:
    def __init__(self, weights: Dict[str, float]):
        self.weights = weights
        self.protocols: Dict[str, ProtocolRisk] = {}

    def add_protocol(self, pr: ProtocolRisk):
        self.protocols[pr.protocol] = pr

    def get_protocol_risk_score(self, protocol: str) -> float:
        return self.protocols[protocol].compute_risk_score(self.weights)

    def get_vault_risk_profile(self, vault_state: VaultState) -> Dict[str, float]:
        exposure = vault_state.protocols
        total = sum(exposure.values())
        weighted_risk = 0.0
        max_risk = 0.0
        for p, a in exposure.items():
            s = a / total
            r = self.get_protocol_risk_score(p)
            weighted_risk += s * r
            max_risk = max(max_risk, r)
        return {
            "weighted_risk": weighted_risk,
            "max_risk": max_risk,
            "total_exposure": total,
            "num_protocols": len(exposure)
        }

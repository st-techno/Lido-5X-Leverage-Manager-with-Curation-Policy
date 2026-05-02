# tests/unit/test_risk_model.py

import pytest
from src.core.risk_model import RiskModel, ProtocolRisk

def test_protocol_risk_score():
    risk = ProtocolRisk(
        protocol="Aave",
        volatility=0.01,
        drawdown_90d=0.15,
        audit_score=1.0,
        tvl=1000000000.0,
        oracle_score=1.0,
        exp_score=1.0
    )
    weights = {"volatility": 0.3, "drawdown": 0.4, "audit": 0.2, "oracle": 0.1, "exp": 0.1}
    score = risk.compute_risk_score(weights)
    assert 0.0 <= score <= 1.0

def test_risk_model_get_vault_risk_profile():
    risk_model = RiskModel(
        weights={"volatility": 0.3, "drawdown": 0.4, "audit": 0.2, "oracle": 0.1, "exp": 0.1}
    )
    risk_model.add_protocol(
        ProtocolRisk("Aave", 0.01, 0.15, 1.0, 1000000000.0, 1.0, 1.0)
    )
    risk_model.add_protocol(
        ProtocolRisk("AVS1", 0.05, 0.3, 0.7, 50000000.0, 0.9, 0.5)
    )

    from src.core.vault_ops import VaultState
    state = VaultState(
        deposited_eth=1000.0,
        staked_eth=4000.0,
        debt_eth=3000.0,
        health_factor=1.5,
        ltvl=0.64,
        loop_factor=4.0,
        protocols={"Aave": 3500.0, "AVS1": 500.0},
        total_exposure=4000.0
    )

    profile = risk_model.get_vault_risk_profile(state)
    assert "weighted_risk" in profile
    assert "max_risk" in profile
    assert profile["max_risk"] > 0.0

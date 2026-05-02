# tests/unit/test_curation_policy.py

import pytest
from src.core.vault_ops import VaultState
from src.curation.curation_params import CurationParams
from src.curation.curation_policy import CurationPolicy
from src.core.risk_model import RiskModel, ProtocolRisk

def test_curation_policy_buffer_violation():
    params = CurationParams(
        max_ltv=0.65,
        min_health_factor=1.30,
        max_loop_factor=4.0,
        max_exposure_per_protocol=0.18,
        max_restaking_avs_exposure=0.15,
        risk_score_cap=0.60,
        rebalance_trigger_offset=0.025,
        unpooled_eth_ratio=0.20,
        emergency_redline_hf=1.10,
        max_rebalance_per_day=1,
        staking_apr=0.04,
        borrowing_apr=0.025
    )

    state = VaultState(
        deposited_eth=1000.0,
        staked_eth=900.0,  # 0.9 > 0.8 → buffer violation
        debt_eth=0.0,
        health_factor=1.5,
        ltvl=0.3,
        loop_factor=0.9,
        protocols={},
        total_exposure=0.0
    )

    policy = CurationPolicy(params)
    errors = policy.check_vault(state, params)

    assert "buffer_violation" in errors

def test_curation_policy_ltv_cap():
    params = CurationParams.load_from_file("config/lido_curation_15dd_20apr.yaml")
    state = VaultState(
        deposited_eth=1000.0,
        staked_eth=4000.0,
        debt_eth=3000.0,
        health_factor=1.25,
        ltvl=0.7,  # 0.7 > 0.65
        loop_factor=4.0,
        protocols={"Aave": 3500.0, "AVS1": 500.0},
        total_exposure=4000.0
    )

    policy = CurationPolicy(params)
    errors = policy.check_vault(state, params)

    assert "ltv_cap" in errors

def test_curation_policy_hf_floor():
    params = CurationParams.load_from_file("config/lido_curation_15dd_20apr.yaml")
    state = VaultState(
        deposited_eth=1000.0,
        staked_eth=4000.0,
        debt_eth=3000.0,
        health_factor=1.2,  # 1.2 < 1.3
        ltvl=0.64,
        loop_factor=4.0,
        protocols={"Aave": 3500.0},
        total_exposure=3500.0
    )

    policy = CurationPolicy(params)
    errors = policy.check_vault(state, params)

    assert "hf_floor" in errors

def test_curation_policy_safe_state():
    params = CurationParams.load_from_file("config/lido_curation_15dd_20apr.yaml")
    state = VaultState(
        deposited_eth=1000.0,
        staked_eth=4000.0,
        debt_eth=3000.0,
        health_factor=1.5,
        ltvl=0.64,
        loop_factor=4.0,
        protocols={"Aave": 3500.0},
        total_exposure=3500.0
    )

    policy = CurationPolicy(params)
    errors = policy.check_vault(state, params)

    assert len(errors) == 0

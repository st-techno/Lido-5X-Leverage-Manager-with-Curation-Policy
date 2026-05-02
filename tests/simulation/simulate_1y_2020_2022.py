# tests/simulation/simulate_1y_2020_2022.py

import random
from src.execution.strategy_executor import run_strategy
from src.chain.chain_adapter import ChainAdapter
from src.curation.curation_params import CurationParams
from src.core.risk_model import RiskModel, ProtocolRisk

def simulate_1y_2020_2022():
    # Set curation params to mimic 2020–2022 crash conditions
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

    # Mock chain adapter (no actual on‑chain TX)
    chain_adapter = ChainAdapter("https://mainnet.infura.io/v3/test", "0x...")

    risk_model = RiskModel(
        weights={"volatility": 0.3, "drawdown": 0.4, "audit": 0.2, "oracle": 0.1, "exp": 0.1}
    )
    risk_model.add_protocol(
        ProtocolRisk("Aave", 0.01, 0.15, 1.0, 1000000000.0, 1.0, 1.0)
    )
    risk_model.add_protocol(
        ProtocolRisk("AVS1", 0.05, 0.3, 0.7, 50000000.0, 0.9, 0.5)
    )

    # Simulate 1 year of 2020–2022‑style crashes (high volatility)
    def make_market_2020_2022(days: int):
        return [
            {
                "ltvl": 0.2 + 0.5 * random.random(),
                "steth_price": 0.8 + 0.4 * random.random(),  # 0.8–1.2 ranges
                "staking_yield": params.staking_apr / 365,
                "borrowing_cost": params.borrowing_apr / 365,
            }
            for _ in range(days)
        ]

    # Run both strategies
    curated = run_strategy("curated", chain_adapter, params, risk_model, num_days=365)
    raw = run_strategy("raw", chain_adapter, params, risk_model, num_days=365)

    # Log results
    print("Curated 1Y 2020–2022:")
    print(f"APR: {curated.get_apr():.2%}, max_drawdown: {curated.max_drawdown:.2%}")

    print("Raw 1Y 2020–2022:")
    print(f"APR: {raw.get_apr():.2%}, max_drawdown: {raw.max_drawdown:.2%}")

    return curated, raw

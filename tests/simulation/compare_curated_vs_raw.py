# tests/simulation/compare_curated_vs_raw.py

import numpy as np
from src.execution.strategy_executor import run_strategy
from src.chain.chain_adapter import ChainAdapter
from src.curation.curation_params import CurationParams
from src.core.risk_model import RiskModel, ProtocolRisk

def compare_curated_vs_raw():
    params = CurationParams.load_from_file("config/lido_curation_15dd_20apr.yaml")
    risk_model = RiskModel(
        weights={"volatility": 0.3, "drawdown": 0.4, "audit": 0.2, "oracle": 0.1, "exp": 0.1}
    )
    risk_model.add_protocol(
        ProtocolRisk("Aave", 0.01, 0.15, 1.0, 1000000000.0, 1.0, 1.0)
    )
    risk_model.add_protocol(
        ProtocolRisk("AVS1", 0.05, 0.3, 0.7, 50000000.0, 0.9, 0.5)
    )

    chain_adapter = ChainAdapter("https://mainnet.infura.io/v3/test", "0x...")

    curated = run_strategy("curated", chain_adapter, params, risk_model, num_days=365)
    raw = run_strategy("raw", chain_adapter, params, risk_model, num_days=365)

    # Compare APR and drawdown
    curated_apr = curated.get_apr()
    raw_apr = raw.get_apr()
    print("Comparison:")
    print(f"Curated APR: {curated_apr:.2%}, max_drawdown: {curated.max_drawdown:.2%}")
    print(f"Raw APR: {raw_apr:.2%}, max_drawdown: {raw.max_drawdown:.2%}")

    # Assert curated < 15% drawdown, raw > 20% drawdown (in 2020‑style crash)
    assert curated.max_drawdown <= 0.15
    assert raw.max_drawdown > 0.20

    return curated, raw

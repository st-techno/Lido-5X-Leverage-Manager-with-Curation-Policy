# tests/unit/test_execution.py

import pytest
from src.execution.strategy_executor import StrategyResult
from src.execution.strategy_executor import run_strategy
from src.chain.chain_adapter import ChainAdapter
from src.curation.curation_params import CurationParams
from src.core.risk_model import RiskModel, ProtocolRisk

def test_run_strategy_curated():
    # Mock chain adapter
    chain_adapter = ChainAdapter("https://mainnet.infura.io/v3/test", "0x...")

    params = CurationParams.load_from_file("config/lido_curation_15dd_20apr.yaml")
    risk_model = RiskModel(
        weights={"volatility": 0.3, "drawdown": 0.4, "audit": 0.2, "oracle": 0.1, "exp": 0.1}
    )
    risk_model.add_protocol(
        ProtocolRisk("Aave", 0.01, 0.15, 1.0, 1000000000.0, 1.0, 1.0)
    )

    result = run_strategy("curated", chain_adapter, params, risk_model, num_days=30)

    assert isinstance(result, StrategyResult)
    assert result.max_drawdown >= 0.0
    assert len(result.market_days) == 30

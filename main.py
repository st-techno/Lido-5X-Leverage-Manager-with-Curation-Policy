# main.py

import random
import logging
from dataclasses import dataclass
from src.curation.curation_params import CurationParams
from src.core.risk_model import RiskModel, ProtocolRisk
from src.chain.chain_adapter import ChainAdapter
from src.execution.strategy_executor import run_strategy
from src.monitor.pnL_tracker import PnLTracker
from src.monitor.metrics import MetricsCollector
from src.monitor.logging import setup_logger, log_json
from src.governance.parameter_updater import update_curation_params
from src.governance.safe_mode import SafeMode

def main():
    # 1. Setup logging
    logger = setup_logger("vault_main")

    # 2. Load config
    curation_params = CurationParams.load_from_file("config/lido_curation_15dd_20apr.yaml")
    logger.info("Loaded curation params")

    # 3. Build risk model
    risk_model = RiskModel(
        weights={"volatility": 0.3, "drawdown": 0.4, "audit": 0.2, "oracle": 0.1, "exp": 0.1}
    )
    risk_model.add_protocol(
        ProtocolRisk("Aave", 0.01, 0.15, 1.0, 1000000000.0, 1.0, 1.0)
    )
    risk_model.add_protocol(
        ProtocolRisk("AVS1", 0.05, 0.3, 0.7, 50000000.0, 0.9, 0.5)
    )
    logger.info("Built risk model")

    # 4. Chain adapter (no actual on‑chain TX for now)
    chain_adapter = ChainAdapter("https://mainnet.infura.io/v3/test", "0x...")

    # 5. Metrics
    metrics = MetricsCollector()

    # 6. Run curated strategy
    metrics.time_start("strategy.curated")
    curated = run_strategy("curated", chain_adapter, curation_params, risk_model, num_days=365)
    metrics.time_end("strategy.curated")

    # 7. Run raw strategy
    metrics.time_start("strategy.raw")
    raw = run_strategy("raw", chain_adapter, curation_params, risk_model, num_days=365)
    metrics.time_end("strategy.raw")

    # 8. Log PnL and drawdown
    tracker = PnLTracker()
    for d in curated.market_days:
        tracker.update(d["pnl"])
    log_json(logger, "Curated P&L and Drawdown",
        pnl=tracker.pnl,
        max_drawdown=tracker.max_drawdown,
        strategy="curated"
    )

    # 9. Export metrics
    with open("metrics.txt", "w") as f:
        f.write(metrics.export_prometheus_text())

    # 10. Compare
    print("Curated APR:", curated.get_apr())
    print("Raw APR:", raw.get_apr())

if __name__ == "__main__":
    main()

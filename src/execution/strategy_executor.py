# src/execution/strategy_executor.py

from typing import Dict, Any
from dataclasses import dataclass
import pandas as pd
from src.strategies.strategy_5x_leverage_raw import Strategy5xRaw
from src.strategies.strategy_5x_leverage_curated import Strategy5xCurated
from src.curation.curation_params import CurationParams
from src.core.vault_ops import VaultState
from src.core.risk_model import RiskModel, ProtocolRisk
from src.chain.chain_adapter import ChainAdapter

@dataclass
class StrategyResult:
    pnl: float
    max_drawdown: float
    final_ltv: float
    final_hf: float
    final_loop_factor: float
    market_days: list

def run_strategy(
    strategy_name: str,
    chain_adapter: ChainAdapter,
    curation_params: CurationParams,
    risk_model: RiskModel,
    num_days: int = 365
) -> StrategyResult:
    if strategy_name == "raw":
        strategy = Strategy5xRaw(seed_eth=1000.0)
    else:
        strategy = Strategy5xCurated(
            params=curation_params,
            risk_model=risk_model,
            seed_eth=1000.0
        )

    market_data = [
        {
            "ltvl": 0.2 + 0.5 * random.random(),
            "steth_price": 1.0,
            "staking_yield": curation_params.staking_apr / 365,
            "borrowing_cost": curation_params.borrowing_apr / 365,
        }
        for _ in range(num_days)
    ]

    daily_results = []
    cum_pnl = 0.0
    running_high = 0.0
    max_drawdown = 0.0

    for mkt in market_data:
        # In production, this would come from chain_adapter.get_vault_state()
        simulated_state = VaultState(
            deposited_eth=1000.0,
            staked_eth=4000.0,
            debt_eth=3000.0,
            health_factor=1.5 + 0.5 * (1.0 - mkt["ltvl"]),
            ltvl=mkt["ltvl"],
            loop_factor=4.0,
            protocols={"Aave": 3500.0, "AVS1": 500.0},
            total_exposure=4000.0,
        )

        if strategy_name == "raw":
            raw_pnl = strategy.run_once(simulated_state, mkt)
            pnl_inc = raw_pnl
        else:
            curated_pnl = strategy.run_once(
                simulated_state, mkt, chain_adapter=chain_adapter
            )
            pnl_inc = curated_pnl

        cum_pnl += pnl_inc
        drawdown = (running_high - cum_pnl) / max(running_high, 1e-6)
        if cum_pnl > running_high:
            running_high = cum_pnl
        if drawdown > max_drawdown:
            max_drawdown = drawdown

        daily_results.append({
            "day": len(daily_results),
            "ltvl": mkt["ltvl"],
            "hf": simulated_state.health_factor,
            "loop_factor": simulated_state.loop_factor,
            "pnl": pnl_inc,
            "cum_pnl": cum_pnl,
            "max_drawdown": max_drawdown,
        })

    return StrategyResult(
        pnl=cum_pnl,
        max_drawdown=max_drawdown,
        final_ltv=daily_results[-1]["ltvl"],
        final_hf=daily_results[-1]["hf"],
        final_loop_factor=daily_results[-1]["loop_factor"],
        market_days=daily_results,
    )

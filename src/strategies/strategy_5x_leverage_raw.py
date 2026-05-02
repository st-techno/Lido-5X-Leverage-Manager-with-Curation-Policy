# src/strategies/strategy_5x_leverage_raw.py

from typing import Dict, Any
from src.core.vault_ops import VaultState
from src.core.market_ops import MarketData

class Strategy5xRaw:
    def __init__(self, seed_eth: float = 1000.0):
        self.seed_eth = seed_eth

    def run_once(self, state: VaultState, market: MarketData) -> float:
        # 1. Compute leverage‑step size (e.g., 0.5 ETH step)
        step_eth = 0.5

        # 2. Simulate increase in leverage (deposit → borrow → re‑stake)
        new_staked = state.staked_eth + step_eth
        new_debt = state.debt_eth + 0.9 * step_eth
        new_ltv = new_debt / new_staked

        # 3. Compute P&L for this step
        base_yield = market["staking_yield"] * new_staked
        cost = market["borrowing_cost"] * new_debt
        return base_yield - cost

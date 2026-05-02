# src/strategies/strategy_5x_leverage_curated.py

from typing import Dict, Any
from src.core.vault_ops import VaultState
from src.curation.curation_policy import CurationPolicy
from src.core.risk_model import RiskModel
from src.execution.strategy_executor import TxReceipt

class Strategy5xCurated:
    def __init__(self, params: Any, risk_model: RiskModel, seed_eth: float = 1000.0):
        self.params = params
        self.risk_model = risk_model
        self.seed_eth = seed_eth
        self.policy = CurationPolicy(params)

    def run_once(self, state: VaultState, market: Dict[str, Any], chain_adapter: Any) -> float:
       

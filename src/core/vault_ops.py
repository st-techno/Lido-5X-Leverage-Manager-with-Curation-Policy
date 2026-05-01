from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class VaultState:
    deposited_eth: float
    staked_eth: float
    debt_eth: float
    health_factor: float
    ltvl: float
    loop_factor: float
    protocols: Dict[str, float]
    total_exposure: float  # sum of protocols.values()

@dataclass
class MarketData:
    ltvl: float
    steth_price: float
    staking_yield: float
    borrowing_cost: float

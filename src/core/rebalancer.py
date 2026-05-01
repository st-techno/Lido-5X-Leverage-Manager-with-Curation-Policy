from typing import Dict, List
from dataclasses import dataclass
import numpy as np

@dataclass
class RebalancePlan:
    old_alloc: np.ndarray
    new_alloc: np.ndarray
    reason: str

class Rebalancer:
    def __init__(self, max_drift: float = 0.025):
        self.max_drift = max_drift

    def compute_target_allocation(self, current_alloc: np.ndarray, protocol_risks: np.ndarray) -> np.ndarray:
        weights = 1.0 / (protocol_risks + 1e-6)
        return weights / weights.sum()

    def needs_rebalance(self, current_alloc: np.ndarray, target_alloc: np.ndarray) -> bool:
        drift = np.abs(current_alloc - target_alloc)
        return drift.max() > self.max_drift

    def propose_rebalance(self, current_alloc: np.ndarray, protocol_risks: np.ndarray) -> RebalancePlan:
        target_alloc = self.compute_target_allocation(current_alloc, protocol_risks)
        if self.needs_rebalance(current_alloc, target_alloc):
            return RebalancePlan(
                old_alloc=current_alloc,
                new_alloc=target_alloc,
                reason="allocation_drift"
            )
        return None

# src/governance/safe_mode.py

from dataclasses import dataclass
from typing import Dict, Any
from src.core.vault_ops import VaultState
from src.curation.curation_policy import CurationPolicy

@dataclass
class SafeMode:
    enabled: bool = False
    emergency_ltv: float = 0.70
    max_loop_factor: float = 2.0

    def is_safe(self, state: VaultState, policy: CurationPolicy, params: Any) -> bool:
        if not self.enabled:
            return True

        if state.ltvl > self.emergency_ltv:
            return False

        if state.loop_factor > self.max_loop_factor:
            return False

        return True

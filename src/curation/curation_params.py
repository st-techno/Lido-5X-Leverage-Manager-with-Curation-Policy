from typing import Dict, Any
from dataclasses import dataclass
import yaml

@dataclass
class CurationParams:
    max_ltv: float
    min_health_factor: float
    max_loop_factor: float
    max_exposure_per_protocol: float
    max_restaking_avs_exposure: float
    risk_score_cap: float
    rebalance_trigger_offset: float
    unpooled_eth_ratio: float
    emergency_redline_hf: float
    max_rebalance_per_day: int
    staking_apr: float
    borrowing_apr: float

    @staticmethod
    def load_from_file(path: str) -> 'CurationParams':
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)["curation"]
        return CurationParams(
            max_ltv=cfg["max_ltv"],
            min_health_factor=cfg["min_health_factor"],
            max_loop_factor=cfg["max_loop_factor"],
            max_exposure_per_protocol=cfg["max_exposure_per_protocol"],
            max_restaking_avs_exposure=cfg["max_restaking_avs_exposure"],
            risk_score_cap=cfg["risk_score_cap"],
            rebalance_trigger_offset=cfg["rebalance_trigger_offset"],
            unpooled_eth_ratio=cfg["unpooled_eth_ratio"],
            emergency_redline_hf=cfg["emergency_redline_hf"],
            max_rebalance_per_day=cfg["max_rebalance_per_day"],
            staking_apr=cfg["staking_apr"],
            borrowing_apr=cfg["borrowing_apr"],
        )

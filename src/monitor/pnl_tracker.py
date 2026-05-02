# src/monitor/pnl_tracker.py

from typing import Dict, Any
import json
import logging
from dataclasses import dataclass

@dataclass
class PnLTracker:
    pnl: float = 0.0
    running_high: float = 0.0
    max_drawdown: float = 0.0
    daily_pnl: list = None

    def __post_init__(self):
        if self.daily_pnl is None:
            self.daily_pnl = []

    def update(self, pnl_inc: float):
        self.pnl += pnl_inc
        self.daily_pnl.append(pnl_inc)

        if self.pnl > self.running_high:
            self.running_high = self.pnl
        else:
            drawdown = (self.running_high - self.pnl) / max(self.running_high, 1e-6)
            if drawdown > self.max_drawdown:
                self.max_drawdown = drawdown

    def save_pnl_history(self, path: str):
        with open(path, "w") as f:
            json.dump({
                "pnl": self.pnl,
                "max_drawdown": self.max_drawdown,
                "daily_pnl": self.daily_pnl
            }, f, indent=2)

    def get_apr(self, years: float = 1.0) -> float:
        if not self.daily_pnl:
            return 0.0
        annual_return = self.pnl
        initial_capital = 1000.0  # should come from config
        return annual_return / initial_capital

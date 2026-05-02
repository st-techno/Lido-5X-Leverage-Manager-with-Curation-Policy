# src/monitor/metrics.py

from typing import Dict, Any
import time

class MetricsCollector:
    def __init__(self):
        self.gauges: Dict[str, float] = {}
        self.counters: Dict[str, float] = {}
        self.timings: Dict[str, list] = {}

    def increment(self, key: str, value: float = 1.0):
        self.counters[key] = self.counters.get(key, 0.0) + value

    def set_gauge(self, key: str, value: float):
        self.gauges[key] = value

    def time_start(self, key: str):
        self.timings[key] = self.timings.get(key, []) + [time.time()]

    def time_end(self, key: str):
        if key in self.timings and self.timings[key]:
            start = self.timings[key].pop()
            elapsed = time.time() - start
            self.gauges[f"{key}_duration_sec"] = elapsed
            self.gauges[f"{key}_rate_per_sec"] = 1.0 / max(elapsed, 1e-6)

    def export_prometheus_text(self) -> str:
        lines = []
        for k, v in self.gauges.items():
            lines.append(f"{k} {v}")
        for k, v in self.counters.items():
            lines.append(f"{k} {v}")
        return "\n".join(lines)

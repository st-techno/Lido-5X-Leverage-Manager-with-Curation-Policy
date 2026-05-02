# src/monitor/logging.py

import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any

def setup_logger(name: str, filename: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    )

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if filename:
        fh = logging.FileHandler(filename)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def log_json(logger: logging.Logger, message: str, **extra: Any):
    record = {
        "@timestamp": datetime.utcnow().isoformat() + "Z",
        "level": "info",
        "message": message,
        **extra,
    }
    logger.info(json.dumps(record, default=str))

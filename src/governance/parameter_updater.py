# src/governance/parameter_updater.py

from typing import Dict, Any
from src.curation.curation_params import CurationParams
import yaml

def update_curation_params(config_path: str, new_params: Dict[str, Any]) -> CurationParams:
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    cfg["curation"].update(new_params)

    with open(config_path, "w") as f:
        yaml.dump(cfg, f, indent=2)

    return CurationParams.load_from_file(config_path)

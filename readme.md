lido_5x_leverage_manager/
├── config/
│   ├── lido_curation_15dd_20apr.yaml          # Curation‑parameters
│   └── vault_settings.yaml                     # Vault‑specific settings (TVL, operators, etc.)
├── src/
│   ├── core/
│   │   ├── vault_ops.py                        # Vault state, helpers
│   │   ├── risk_model.py                       # Protocol risk‑model
│   │   └── rebalancer.py                       # Rebalance logic
│   ├── curation/
│   │   ├── curation_params.py                 # Curation‑params (YAML loader)
│   │   ├── curation_guard.py                  # @with_curation_guard decorator
│   │   └── curation_policy.py                 # Central policy engine
│   ├── execution/
│   │   ├── tx_builder.py                      # Build Aave‑style txs
│   │   └── strategy_executor.py               # Run strategy with real‑chain actions
│   ├── chain/
│   │   ├── chain_adapter.py                   # Web3‑to‑contract adapter
│   │   └── aave_lido_interop.py               # Aave + Lido wrappers
│   ├── monitor/
│   │   ├── pnl_tracker.py                     # Track P&L, drawdown
│   │   ├── metrics.py                         # Prometheus‑style metrics
│   │   └── logging.py                         # Structured JSON logging
│   ├── governance/
│   │   ├── parameter_updater.py               # Governance‑parameter updates
│   │   └── safe_mode.py                       # Safe‑mode / emergency‑mode logic
│   └── strategies/
│       ├── strategy_5x_leverage_raw.py        # Non‑curated 5x‑loop
│       └── strategy_5x_leverage_curated.py    # Lido‑curation‑guarded 5x‑loop
├── tests/
│   ├── unit/
│   │   ├── test_curation_policy.py
│   │   ├── test_risk_model.py
│   │   └── test_execution.py
│   └── simulation/
│       ├── simulate_1y_2020_2022.py
│       └── compare_curated_vs_raw.py
└── main.py                                      # CLI entry

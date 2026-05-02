## Lido‑5x‑Leverage‑Manager production code:

## Features

The vault is a Lido‑style 5x‑leveraged ETH‑stETH‑Aave‑loop that turns fresh ETH deposits into a highly‑leveraged stETH position, borrowing against ETH‑stETH collateral to boost yield, while enforcing strict risk‑factor caps and buffer‑style reserve‑ratio checks.

Core configuration is driven by config/lido_curation_15dd_20apr.yaml, which defines max‑DD ≈15% and target APR ≈20% through parameters like max_ltv: 0.65, min_health_factor: 1.30, max_loop_factor: 4.0, and max_restaking_avs_exposure: 0.15.

src/core/vault_ops.py defines VaultState, which holds deposited_eth, staked_eth, debt_eth, health_factor, ltvl, loop_factor, and a protocols dict for tracking exposure per‑protocol (e.g., Aave, AVS‑style legs).

src/core/risk_model.py introduces a RiskModel that computes a risk_score per‑protocol using volatility, drawdown, audit, oracle, and experience scores, then aggregates max_risk and weighted_risk for the whole vault, enforcing risk_score_cap: 0.60 in config/.

src/curation/curation_policy.py implements Lido‑style curation‑logic as CurationPolicy: it checks buffer‑ratio (unpooled_eth_ratio: 0.20), LTV cap, health‑factor floor, loop‑factor cap, per‑protocol exposure cap, AVS‑exposure cap, and max_risk cap, returning unsafe errors if any bound is breached.

src/curation/curation_guard.py offers @with_curation_guard, a decorator that wraps strategy methods and blocks execution when CurationPolicy rules are violated or max_risk exceeds risk_score_cap, ensuring that no transaction (deposit, borrow, rebalance) proceeds in an unsafe state.

src/core/rebalancer.py enforces “rebalance‑only‑on‑risk‑drift” logic: Rebalancer computes inverse‑risk‑weighted target allocations, and only triggers RebalancePlan when drift exceeds rebalance_trigger_offset: 0.025 (2.5%); this mimics Lido‑style RR‑buffer‑style rebalancing.

Strategies live in src/strategies/:

strategy_5x_leverage_raw.py defines Strategy5xRaw, which blindly increases leverage without any curation‑guard, serving as a naive 5x‑loop baseline for APR‑drawdown comparison.

strategy_5x_leverage_curated.py defines Strategy5xCurated, which, on each run_once, first consults CurationPolicy and RiskModel, then either skips leverage, rebalances, or executes a single 5x‑loop‑step (via aave_lido_interop.py‑style ETH→stETH→Aave‑borrow) depending on current state.

src/execution/strategy_executor.py encapsulates run_strategy, which runs either "curated" or "raw" over num_days (by default 365), simulating daily market data, calling the strategy’s run_once, and accumulating pnl, max_drawdown, final_ltv, final_hf, and final_loop_factor into StrategyResult.

src/chain/chain_adapter.py provides a ChainAdapter that connects to Ethereum‑mainnet via web3, exposes get_vault_state (stubbed in simulation), and wraps real‑on‑chain calls to Lido.stETH (stake) and Aave‑style lending pools (deposit_steth, borrow_eth).

src/chain/aave_lido_interop.py defines perform_5x_loop, which iteratively deposits ETH to Lido, deposits stETH to Aave, and borrows ETH until loop_factor ≈ 4.0, returning an updated VaultState with new staked_eth, debt_eth, ltvl, and health_factor.

Monitoring is structured under src/monitor/:

pnl_tracker.py uses PnLTracker to track cumulative P&L, max‑drawdown, and daily P&L, exporting JSON history suitable for analytics dashboards.

metrics.py implements MetricsCollector that exposes Prometheus‑style gauges and counters (e.g., vault_pnl, vault_rebalance_count, strategy.curated_duration_sec).

logging.py configures setup_logger and log_json for structured JSON logging of strategy‑state and P&L.

Governance tools live in src/governance/:

parameter_updater.py exposes update_curation_params that writes new YAML‑style curation settings and rebuilds CurationParams objects, enabling dynamic risk‑factor rotation without redeploying code.

safe_mode.py provides SafeMode with emergency_ltv and max_loop_factor caps, which can be toggled to enforce extra‑tight constraints during black‑swan‑style crashes.

Tests under tests/unit/ verify curation_policy, risk_model, and strategy_executor in isolation, while tests/simulation/ modules (simulate_1y_2020_2022.py, compare_curated_vs_raw.py) run 1‑year simulations, assert that curated.max_drawdown ≤ 0.15 and raw.max_drawdown > 0.20, and compare APRs.

main.py is the CLI entrypoint that instantiates CurationParams, RiskModel, and ChainAdapter, runs both curated and raw strategies, logs structured JSON‑P&L and Prometheus‑metrics, and prints APR‑drawdown comparisons, ready to be wired into a 24/7 daemon that periodically rebalances and reports to Prometheus + Grafana.

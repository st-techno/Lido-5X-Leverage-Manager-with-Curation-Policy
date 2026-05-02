## Code Execution Flow

This vault uses **Lido‑style curation** over a 5x‑leveraged ETH‑stETH‑loop on Aave‑like protocols.

```mermaid
sequenceDiagram
    participant CLI as "CLI : python main.py"
    participant Main as "main.py"
    participant StrExec as "strategy_executor.run_strategy"
    participant CurStrat as "Strategy5xCurated"
    participant RawStrat as "Strategy5xRaw"
    participant Chain as "chain.ChainAdapter"
    participant Curation as "curation.CurationPolicy"
    participant RiskModel as "risk_model.RiskModel"
    participant Tests as "tests/simulation/compare_curated_vs_raw.py"

    CLI->>Main: main()

    Main->>Main: setup_logger("vault_main")
    Main->>Main: params = CurationParams.load_from_file(...)
    Main->>Main: risk_model.add_protocol(Aave, AVS1)
    Main->>Main: chain_adapter = ChainAdapter("rpc_url", "key")

    %% Curated strategy
    Main->>StrExec: run_strategy("curated", chain_adapter, params, risk_model, 365)
    activate StrExec

    loop day = 0 to 364
        StrExec->>Chain: get_vault_state()
        Chain-->>StrExec: VaultState(deposited_eth, staked_eth, debt_eth, ltvl, ...)

        StrExec->>CurStrat: run_once(state, market, chain_adapter)
        activate CurStrat

        CurStrat->>Curation: policy.check_vault(state, params)
        activate Curation
        opt if errors not empty
            Curation-->>CurStrat: unsafe errors
            CurStrat-->>StrExec: return 0.0 (no new leverage)
        else
            Curation-->>CurStrat: safe
            CurStrat->>Curation: policy.check_rebalance(...)
            activate Curation
            Curation->>RiskModel: get_vault_risk_profile()
            activate RiskModel
            RiskModel-->>Curation: {max_risk, weighted_risk, ...}
            deactivate RiskModel

            opt if reb_status = "need_rebalance"
                CurStrat->>Rebalancer: propose_rebalance(...)
                CurStrat->>Chain: rebalance_deployment(old_alloc, new_alloc)
                activate Chain
                Chain-->>StrExec: TxReceipt: "success"
                deactivate Chain
            end

            CurStrat->>Chain: perform_5x_loop(increase_eth)
            activate Chain
            Chain->>Chain: deposit_eth_to_steth(...)
            Chain->>Chain: deposit_steth_to_aave(...)
            Chain->>Chain: borrow_eth_from_aave(...)
            Chain-->>CurStrat: new VaultState(staked_eth, debt_eth, ltvl, hf, loop_factor)
            deactivate Chain

            CurStrat->>CurStrat: compute P&L = staking_yield * staked_eth - borrow_cost * debt_eth
            CurStrat-->>StrExec: return pnl
        end
        deactivate CurStrat
    end

    StrExec-->>Main: StrategyResult (curated)

    %% Raw strategy
    Main->>StrExec: run_strategy("raw", chain_adapter, params, risk_model, 365)
    activate StrExec

    loop day = 0 to 364
        StrExec->>Chain: get_vault_state()
        Chain-->>StrExec: VaultState

        StrExec->>RawStrat: run_once(state, market)
        activate RawStrat
        RawStrat->>RawStrat: toy leverage step (no curation)
        RawStrat->>RawStrat: compute pnl
        RawStrat-->>StrExec: return pnl
        deactivate RawStrat
    end

    StrExec-->>Main: StrategyResult (raw)

    Main->>Main: PnLTracker.update(day_pnl)
    Main->>Main: metrics.export_prometheus_text() -> "metrics.txt"
    Main->>Main: print APR_curated, APR_raw

    deactivate StrExec

    %% Test comparison layer
    Tests->>Tests: compare_curated_vs_raw()
    activate Tests

    Tests->>StrExec: run_strategy("curated", ..., 365)
    Tests->>StrExec: run_strategy("raw", ..., 365)
    StrExec-->>Tests: curated_result, raw_result

    Tests->>Tests: assert curated.max_drawdown ≤ 0.15
    Tests->>Tests: assert raw.max_drawdown > 0.20
    Tests->>Tests: print APR comparison

    deactivate Tests
```

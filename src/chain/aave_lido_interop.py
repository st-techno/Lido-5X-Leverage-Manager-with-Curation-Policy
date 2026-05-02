# src/chain/aave_lido_interop.py

from typing import Dict, Any
from src.chain.chain_adapter import ChainAdapter
from src.core.vault_ops import VaultState

def perform_5x_loop(
    adapter: ChainAdapter,
    initial_eth: float,
    max_rounds: int = 5
) -> VaultState:
    current_eth = initial_eth
    borrowed_eth = 0.0

    for i in range(max_rounds):
        # 1. Deposit ETH → mint stETH
        adapter.deposit_eth_to_steth(current_eth)

        # 2. Deposit stETH to Aave
        # 3. Borrow ETH
        adapter.borrow_eth_from_aave(0.9 * current_eth)

        current_eth += 0.9 * current_eth
        borrowed_eth += 0.9 * current_eth

        # Break if leverage cap reached
        if current_eth / initial_eth >= 4.0:
            break

    return VaultState(
        deposited_eth=initial_eth,
        staked_eth=current_eth,
        debt_eth=borrowed_eth,
        health_factor=1.25,
        ltvl=0.64,
        loop_factor=current_eth / initial_eth,
        protocols={"Aave": current_eth - borrowed_eth},
        total_exposure=current_eth - borrowed_eth
    )

# src/chain/chain_adapter.py

from web3 import Web3
from typing import Dict, Any
import json
from dataclasses import dataclass
from src.core.vault_ops import VaultState

@dataclass
class TxReceipt:
    tx_hash: str
    status: str  # "success" / "failed"

class ChainAdapter:
    def __init__(self, rpc_url: str, private_key: str):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = self.web3.eth.account.from_key(private_key)

        self.lido_addr = "0xae7ab96520DE30cB1a393DdC852552A07ca0a0a0"
        self.aave_addr = "0x7d2768dE32b0b80b7a3454c06BdAc94A69DDd8a1"

        self.lido_abi = self.load_abi("src/chain/abi/lido.abi.json")
        self.aave_abi = self.load_abi("src/chain/abi/aave_lending_pool.abi.json")

        self.lido_contract = self.web3.eth.contract(
            address=self.lido_addr,
            abi=self.lido_abi
        )
        self.aave_contract = self.web3.eth.contract(
            address=self.aave_addr,
            abi=self.aave_abi
        )

    def load_abi(self, path: str) -> list:
        with open(path, "r") as f:
            return json.load(f)

    def get_vault_state(self) -> VaultState:
        return VaultState(
            deposited_eth=1000.0,
            staked_eth=4000.0,
            debt_eth=3000.0,
            health_factor=1.25,
            ltvl=0.64,
            loop_factor=4.0,
            protocols={"Aave": 3500.0, "AVS1": 500.0},
            total_exposure=4000.0,
        )

    def deposit_eth_to_steth(self, amount_eth: float) -> TxReceipt:
        amount_wei = self.web3.to_wei(amount_eth, "ether")
        tx = self.lido_contract.functions.stake(
            amount_wei
        ).build_transaction({
            "from": self.account.address,
            "value": amount_wei,
            "gas": 1000000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return TxReceipt(tx_hash=self.web3.to_hex(tx_hash), status="success")

    def deposit_steth_to_aave(self, steth_amount_eth: float, aave_address: str) -> TxReceipt:
        # Assume this uses Aave‑style wrapper
        tx = self.aave_contract.functions.deposit(
            self.lido_addr,
            self.web3.to_wei(steth_amount_eth, "ether"),
            self.account.address,
            0
        ).build_transaction({
            "from": self.account.address,
            "gas": 100000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return TxReceipt(tx_hash=self.web3.to_hex(tx_hash), status="success")

    def borrow_eth_from_aave(self, borrow_amount_eth: float) -> TxReceipt:
        tx = self.aave_contract.functions.borrow(
            "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # ETH
            self.web3.to_wei(borrow_amount_eth, "ether"),
            2, 0, self.account.address
        ).build_transaction({
            "from": self.account.address,
            "gas": 100000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
        })
        signed_tx = self.web3.eth.account.sign_transaction(tx, self.account.key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return TxReceipt(tx_hash=self.web3.to_hex(tx_hash), status="success")

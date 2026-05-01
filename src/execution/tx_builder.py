from typing import Dict, Any, List
from dataclasses import dataclass
from web3 import Web3
import json

@dataclass
class Transaction:
    to: str
    data: str
    value: int
    gas: int
    gas_price: int

class TxBuilder:
    def __init__(self, web3: Web3, private_key: str):
        self.web3 = web3
        self.account = web3.eth.account.from_key(private_key)

    def deposit_eth_to_steth(self, amount_wei: int) -> Transaction:
        # Example: call Lido.stake(uint256)
        contract = self.web3.eth.contract(
            address="0xae7ab96520DE30cB1a393DdC852552A07ca0a0a0",
            abi=json.loads("..."),  # Lido ABI
        )
        tx = contract.functions.stake(amount_wei).build_transaction({
            "from": self.account.address,
            "value": amount_wei,
            "gas": 1000000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
        })
        return Transaction(
            to=tx["to"],
            data=tx["data"],
            value=tx["value"],
            gas=tx["gas"],
            gas_price=tx["gasPrice"],
        )

    def approve_steth_to_aave(self, steth_amount: int, aave_address: str) -> Transaction:
        # Approve stETH to Aave pool
        contract = self.web3.eth.contract(
            address="0xae7ab96520DE30cB1a393DdC852552A07ca0a0a0",
            abi=json.loads("..."),  # Lido ERC20‑style ABI
        )
        tx = contract.functions.approve(aave_address, steth_amount).build_transaction({
            "from": self.account.address,
            "gas": 100000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
        })
        return Transaction(
            to=tx["to"],
            data=tx["data"],
            value=tx["value"],
            gas=tx["gas"],
            gas_price=tx["gasPrice"],
        )

    def deposit_steth_to_aave(self, aave_address: str, steth_amount: int) -> Transaction:
        # Assuming Aave‑style lending pool method
        contract = self.web3.eth.contract(
            address=aave_address,
            abi=json.loads("..."),  # Aave LendingPool ABI
        )
        tx = contract.functions.deposit(
            "0xae7ab96520DE30cB1a393DdC852552A07ca0a0a0",  # stETH addr
            steth_amount, 0,
        ).build_transaction({
            "from": self.account.address,
            "gas": 100000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
        })
        return Transaction(
            to=tx["to"],
            data=tx["data"],
            value=tx["value"],
            gas=tx["gas"],
            gas_price=tx["gasPrice"],
        )

    def borrow_eth_from_aave(self, aave_address: str, amount_wei: int) -> Transaction:
        contract = self.web3.eth.contract(
            address=aave_address,
            abi=json.loads("..."),
        )
        tx = contract.functions.borrow(
            "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # ETH address
            amount_wei, 2, 0, self.account.address
        ).build_transaction({
            "from": self.account.address,
            "gas": 100000,
            "gasPrice": self.web3.eth.gas_price,
            "nonce": self.web3.eth.get_transaction_count

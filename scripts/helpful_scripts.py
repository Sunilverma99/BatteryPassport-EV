# scripts/helpful_scripts.py

from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
)
from web3 import Web3

DECIMALS = 8
STARTING_PRICE = 1000 * 10 ** DECIMALS  # Mock ETH/GBP price

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None, id=None):
    """
    Returns the account to use for deployments and transactions.
    """
    if index is not None:
        return accounts[index]
    if id is not None:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]  # Use the first Ganache account
    return accounts.add(config["wallets"]["from_key"])

def deploy_mocks():
    """
    Deploys mock contracts for local testing.
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(
            DECIMALS,
            STARTING_PRICE,
            {"from": account},
        )
    print("Mocks Deployed!")

def get_contract(contract_name):
    """
    Retrieves the contract instance for a given contract name.
    """
    contract_type = {
        "eth_gbp_price_feed": MockV3Aggregator,
    }[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) == 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(
            contract_type._name,
            contract_address,
            contract_type.abi,
        )
    return contract

from brownie import MockV3Aggregator
from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    Contract,
)
from web3 import Web3

# Align DECIMALS and STARTING_PRICE with deploy.py
DECIMALS = 18
STARTING_PRICE = 2000 * 10 ** DECIMALS  # Mock ETH/GBP price set to 2000 GBP per ETH

# Define local and forked environments
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

def get_account(index=None, id=None):
    """
    Returns the appropriate account based on the network.
    """
    if index is not None:
        return accounts[index]
    if id is not None:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]  # Use the first Ganache account for local networks
    return accounts.add(config["wallets"]["from_key"])  # Use account from config for live networks

def deploy_mocks():
    """
    Deploys mock contracts for local testing if not already deployed.
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
        print("MockV3Aggregator deployed!")
    else:
        print("MockV3Aggregator already deployed!")
    
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

# scripts/deploy.py
from brownie import MockV3Aggregator
from brownie import EVBatteryPassport, MockV3Aggregator, network, config
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from brownie.network.contract import Contract

def deploy_ev_battery_passport():
    """
    Deploys the EVBatteryPassport contract.

    - Deploys mock contracts if on a local network.
    - Retrieves the appropriate price feed address.
    - Assumes the deployer account is the government.

    Returns:
        EVBatteryPassport: The deployed EVBatteryPassport contract instance.
    """
    account = get_account()
    
    # Deploy mocks if on a local blockchain
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        print("Local network detected! Deploying mocks...")
        deploy_mocks()
        price_feed = MockV3Aggregator[-1]
        price_feed_address = price_feed.address
    else:
        # Use the real price feed address from config
        price_feed_address = config["networks"][network.show_active()]["eth_gbp_price_feed"]
    
    # Government address is the deployer account
    government_address = account.address
    
    # Deploy the EVBatteryPassport contract
    print(f"Deploying EVBatteryPassport from account {account}...")
    ev_battery_passport = EVBatteryPassport.deploy(
        government_address,
        price_feed_address,
        {"from": account, "gas_limit": 3000000},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    
    print(f"EVBatteryPassport deployed at {ev_battery_passport.address}")
    return ev_battery_passport

def main():
    """
    The main function that Brownie calls when deploying.
    """
    deploy_ev_battery_passport()

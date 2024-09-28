# scripts/deploy.py

from brownie import EVBatteryPassport, MockV3Aggregator, network
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)

def deploy_ev_battery_passport():
    account = get_account()
    # If we're on a local blockchain, deploy mocks
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address
    else:
        # Use the real price feed address from config
        price_feed_address = config["networks"][network.show_active()]["eth_gbp_price_feed"]

    # Assume the deployer is the government
    government_address = account.address

    ev_battery_passport = EVBatteryPassport.deploy(
        government_address,
        price_feed_address,
        {"from": account},
        publish_source=False,  # No need to verify on local network
    )
    print(f"Contract deployed at {ev_battery_passport.address}")
    return ev_battery_passport

def main():
    deploy_ev_battery_passport()

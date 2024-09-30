import pytest
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts, exceptions, Wei
from web3 import Web3
from web3.exceptions import BadResponseFormat

def test_erc721_functionality(ev_battery_passport, government_account, manufacturer_account, consumer_account):
    """Test basic ERC721 functionality and battery data setting."""
    print("\n--- ERC721 Functionality Test ---")

    # Add manufacturer and set up deposit
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': Wei("1 ether")})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})
    print("Manufacturer added and deposit locked")

    # Set battery data and mint token
    token_id = 1
    tx = ev_battery_passport.setBatteryData(
        token_id,
        "Model Y",
        "Location B",
        "NiMH",
        "Hybrid Battery",
        {'from': manufacturer_account}
    )
    print(f"\nToken {token_id} minted with battery data")

    # Test minting (setBatteryData implicitly mints a token)
    owner = ev_battery_passport.ownerOf(token_id)
    print(f"Token {token_id} owner: {owner}")
    assert owner == manufacturer_account

    # Verify BatteryDataSet event
    print("\nBattery Data Set Event:")
    print(f"Token ID: {tx.events['BatteryDataSet']['tokenId']}")
    print(f"Manufacturer: {tx.events['BatteryDataSet']['manufacturer']}")
    print(f"Battery Model: {tx.events['BatteryDataSet']['batteryModel']}")
    print(f"Battery Type: {tx.events['BatteryDataSet']['batteryType']}")
    print(f"Product Name: {tx.events['BatteryDataSet']['productName']}")

    # Test transferring
    ev_battery_passport.transferFrom(manufacturer_account, consumer_account, token_id, {'from': manufacturer_account})
    new_owner = ev_battery_passport.ownerOf(token_id)
    print(f"\nToken {token_id} transferred to {new_owner}")
    assert new_owner == consumer_account

    # Verify battery data
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})
    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(token_id, {'from': consumer_account})
    
    print("\nBattery Details:")
    print(f"Battery Type: {batteryType}")
    print(f"Battery Model: {batteryModel}")
    print(f"Product Name: {productName}")
    print(f"Manufacturing Site: {manufacturingSite}")

    # Test minting a token with a different ID
    
    # Test minting a token with a different ID
    new_token_id = 2
    tx = ev_battery_passport.setBatteryData(
    new_token_id,
    "Model Z",
    "Location C",
    "Li-ion",
    "Electric Car Battery",
    {'from': manufacturer_account}
)
    print(f"\nNew token {new_token_id} minted")
    new_token_owner = ev_battery_passport.ownerOf(new_token_id)
    print(f"Token {new_token_id} owner: {new_token_owner}")
    assert new_token_owner == manufacturer_account

# Verify BatteryDataSet event for Token 2
    print(f"\nBattery Data Set Event for Token {new_token_id}:")
    print(f"Token ID: {tx.events['BatteryDataSet']['tokenId']}")
    print(f"Manufacturer: {tx.events['BatteryDataSet']['manufacturer']}")
    print(f"Battery Model: {tx.events['BatteryDataSet']['batteryModel']}")
    print(f"Battery Type: {tx.events['BatteryDataSet']['batteryType']}")
    print(f"Product Name: {tx.events['BatteryDataSet']['productName']}")

    # Grant CONSUMER_ROLE to manufacturer_account (if needed for viewing details)
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), manufacturer_account, {'from': government_account})

    # Retrieve and display battery details for Token 2
    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(new_token_id, {'from': manufacturer_account})
    print(f"\nToken {new_token_id} Details:")
    print(f"Battery Type: {batteryType}")
    print(f"Battery Model: {batteryModel}")
    print(f"Product Name: {productName}")
    print(f"Manufacturing Site: {manufacturingSite}")

    print("\n--- ERC721 Functionality Test Completed ---")
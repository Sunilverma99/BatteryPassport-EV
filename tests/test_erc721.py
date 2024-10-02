import pytest
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts, exceptions, Wei
from web3 import Web3

def test_erc721_functionality(ev_battery_passport, government_account, manufacturer_account, consumer_account):
    """Test basic ERC721 functionality and battery data setting."""

    # Add manufacturer and set up deposit
    print("\n=== Adding Manufacturer ===")
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    print(f"Manufacturer added: {manufacturer_account}")

    print("\n=== Depositing Funds ===")
    deposit_amount = Wei("1 ether")
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': deposit_amount})
    print(f"Funds deposited: {deposit_amount} wei")

    print("\n=== Locking Deposit ===")
    ev_battery_passport.lockDeposit({'from': manufacturer_account})
    print("Deposit locked.")

    # Set battery data and mint token
    token_id = 1
    print("\n=== Setting Battery Data ===")
    tx = ev_battery_passport.setBatteryData(
        token_id,
        "Model Y",
        "USA",
        "NiMH",
        "Hybrid Battery",
        {'from': manufacturer_account}
    )

    # Test minting (setBatteryData implicitly mints a token)
    owner = ev_battery_passport.ownerOf(token_id)
    assert owner == manufacturer_account
    print(f"Token ID {token_id} minted to: {owner}")

    # Verify BatteryDataSet event
    print("\n=== Verifying BatteryDataSet Event ===")
    assert 'BatteryDataSet' in tx.events
    assert tx.events['BatteryDataSet']['tokenId'] == token_id
    assert tx.events['BatteryDataSet']['manufacturer'] == manufacturer_account
    assert tx.events['BatteryDataSet']['batteryModel'] == "Model Y"
    assert tx.events['BatteryDataSet']['batteryType'] == "NiMH"
    assert tx.events['BatteryDataSet']['productName'] == "Hybrid Battery"
    print("BatteryDataSet event verified.")

    # Test transferring
    print("\n=== Transferring Token ===")
    ev_battery_passport.transferFrom(manufacturer_account, consumer_account, token_id, {'from': manufacturer_account})
    assert ev_battery_passport.ownerOf(token_id) == consumer_account
    print(f"Token ID {token_id} transferred to: {consumer_account}")

    # Verify battery data
    print("\n=== Granting Consumer Role ===")
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})
    print(f"Consumer role granted to: {consumer_account}")

    print("\n=== Viewing Battery Details ===")
    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(token_id, {'from': consumer_account})
    assert batteryType == "NiMH"
    assert batteryModel == "Model Y"
    assert productName == "Hybrid Battery"
    assert manufacturingSite == "USA"
    print(f"Battery details - Type: {batteryType}, Model: {batteryModel}, Product: {productName}, Location: {manufacturingSite}")

    # Test minting a token with a different ID (should succeed)
    new_token_id = 2  # Different token ID
    print("\n=== Setting New Battery Data ===")
    tx = ev_battery_passport.setBatteryData(
        new_token_id,
        "Model Z",
        "USA",
        "Li-ion",
        "Electric Car Battery",
        {'from': manufacturer_account}
    )
    
    assert ev_battery_passport.ownerOf(new_token_id) == manufacturer_account
    print(f"Token ID {new_token_id} minted to: {manufacturer_account}")

    # View and print details for the new token ID
    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(new_token_id, {'from': consumer_account})
    print(f"New Battery details - Type: {batteryType}, Model: {batteryModel}, Product: {productName}, Location: {manufacturingSite}")

    print("=== Test Completed Successfully ===")

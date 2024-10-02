import pytest
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts, exceptions, Wei
from web3 import Web3

@pytest.fixture
def government_account():
    return accounts[0]

@pytest.fixture
def manufacturer_account():
    return accounts[1]

@pytest.fixture
def supplier_account():
    return accounts[2]

@pytest.fixture
def consumer_account():
    return accounts[3]

@pytest.fixture
def recycler_account():
    return accounts[4]

def test_erc721_functionality(ev_battery_passport, government_account, manufacturer_account, supplier_account, recycler_account, consumer_account):
    """Test ERC721 functionality from government to manufacturer, supplier, consumer, recycler, and back to manufacturer."""

    # Government adds manufacturer and manufacturer locks deposit
    print("Adding manufacturer and setting up deposit...")
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})

    # Get the minimum deposit required in Wei
    min_deposit_in_wei = ev_battery_passport.calculateMinDeposit({'from': government_account})
    print(f"Minimum deposit required is {min_deposit_in_wei} Wei.")

    # Manufacturer deposits the minimum required amount
    print(f"Manufacturer locking deposit of {min_deposit_in_wei} Wei...")
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': min_deposit_in_wei})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})
    print(f"Manufacturer {manufacturer_account} added and deposit locked.")

    # Manufacturer sets battery data and mints token
    token_id = 1
    print(f"Setting battery data for token {token_id}...")
    tx = ev_battery_passport.setBatteryData(
        token_id,
        "Model Y",
        "Location B",
        "NiMH",
        "Hybrid Battery",
        {'from': manufacturer_account}
    )
    print(f"Battery data set for token {token_id} and token minted.")

    # Test minting (setBatteryData implicitly mints a token)
    assert ev_battery_passport.ownerOf(token_id) == manufacturer_account
    print(f"Token {token_id} is owned by {manufacturer_account}.")

    # Verify BatteryDataSet event
    assert 'BatteryDataSet' in tx.events
    assert tx.events['BatteryDataSet']['tokenId'] == token_id
    print(f"Verified BatteryDataSet event for token {token_id}.")

    # Manufacturer transfers battery to supplier
    print(f"Transferring token {token_id} from manufacturer {manufacturer_account} to supplier {supplier_account}...")
    ev_battery_passport.transferFrom(manufacturer_account, supplier_account, token_id, {'from': manufacturer_account})
    assert ev_battery_passport.ownerOf(token_id) == supplier_account
    print(f"Token {token_id} successfully transferred to supplier {supplier_account}.")

    # Supplier updates supply chain info
    print("Granting supplier role and updating supply chain info...")
    ev_battery_passport.grantRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
    supply_chain_data = "Shipped from Factory B to Distribution Center C"
    tx = ev_battery_passport.updateSupplyChainInfo(token_id, supply_chain_data, {'from': supplier_account})

    # Verify SupplyChainInfoUpdated event
    assert 'SupplyChainInfoUpdated' in tx.events
    print(f"Supply chain info updated for token {token_id} by supplier {supplier_account}.")

    # Supplier transfers battery to consumer
    print(f"Transferring token {token_id} from supplier {supplier_account} to consumer {consumer_account}...")
    ev_battery_passport.transferFrom(supplier_account, consumer_account, token_id, {'from': supplier_account})
    assert ev_battery_passport.ownerOf(token_id) == consumer_account
    print(f"Token {token_id} successfully transferred to consumer {consumer_account}.")

    # Consumer views battery details
    print("Granting consumer role and verifying battery details...")
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

    # Ensure viewBatteryDetails function can be called
    batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer = ev_battery_passport.viewBatteryDetails(token_id, {'from': consumer_account})

    assert batteryType == "NiMH"
    assert batteryModel == "Model Y"
    assert productName == "Hybrid Battery"
    assert manufacturingSite == "Location B"
    assert supplyChainInfo == "Shipped from Factory B to Distribution Center C"
    assert isRecycled == False

    # Print out values obtained from viewBatteryDetails
    print("=== Battery Details ===")
    print(f"Battery Type: {batteryType}")
    print(f"Battery Model: {batteryModel}")
    print(f"Product Name: {productName}")
    print(f"Manufacturing Site: {manufacturingSite}")
    print(f"Supply Chain Info: {supplyChainInfo}")
    print(f"Recycled: {'Yes' if isRecycled else 'No'}")
    print(f"Returned to Manufacturer: {'Yes' if returnedToManufacturer else 'No'}")

    # Consumer transfers battery to recycler
    print(f"Transferring token {token_id} from consumer {consumer_account} to recycler {recycler_account}...")
    ev_battery_passport.transferFrom(consumer_account, recycler_account, token_id, {'from': consumer_account})
    assert ev_battery_passport.ownerOf(token_id) == recycler_account
    print(f"Token {token_id} successfully transferred to recycler {recycler_account}.")

    # Recycler marks battery as recycled
    print("Granting recycler role and marking the battery as recycled...")
    ev_battery_passport.grantRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account, {'from': government_account})
    ev_battery_passport.markBatteryRecycled(token_id, {'from': recycler_account})

    # Verify the battery is marked as recycled
    print("Verifying recycler can view battery details...")
    
    # Check if the recycler has the correct role
    assert ev_battery_passport.hasRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account), "Recycler doesn't have the RECYCLER_ROLE"

    # Grant additional roles if necessary (e.g., if CONSUMER_ROLE is required to view details)
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), recycler_account, {'from': government_account})
    
    # Now the recycler can view battery details
    batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer = ev_battery_passport.viewBatteryDetails(token_id, {'from': recycler_account})

    assert batteryType == "NiMH"
    assert batteryModel == "Model Y"
    assert productName == "Hybrid Battery"
    assert manufacturingSite == "Location B"
    assert supplyChainInfo == "Shipped from Factory B to Distribution Center C"
    assert isRecycled == True
    print(f"Verified battery details for token {token_id} after marking as recycled.")

    # Additional check: Verify that the government account can also view the details
    print("Verifying government can view battery details...")
    govBatteryType, _, _, _, _, govIsRecycled, _ = ev_battery_passport.viewBatteryDetails(token_id, {'from': government_account})
    assert govBatteryType == "NiMH"
    assert govIsRecycled == True
    print("Government successfully viewed battery details.")

    print("ERC721 functionality test completed successfully.")
    
    # Create a second token with different data
    token_id_2 = 2
    ev_battery_passport.setBatteryData(
        token_id_2,
        "Model X",
        "Location C",
        "Li-ion",
        "Electric Vehicle Battery",
        {'from': manufacturer_account}
    )
    ev_battery_passport.transferFrom(manufacturer_account, supplier_account, token_id_2, {'from': manufacturer_account})
    ev_battery_passport.updateSupplyChainInfo(token_id_2, "Shipped from Factory C to Distribution Center D", {'from': supplier_account})

    # Final summary print statement
    print("\n=== EV Battery Passport Summary ===")
    
    def get_owner_name(address):
        if address == government_account:
            return "Government"
        elif address == manufacturer_account:
            return "Manufacturer"
        elif address == supplier_account:
            return "Supplier"
        elif address == recycler_account:
            return "Recycler"
        elif address == consumer_account:
            return "Consumer"
        else:
            return "Unknown"

    for token_id in [1, 2]:
        batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer = ev_battery_passport.viewBatteryDetails(token_id, {'from': government_account})
        current_owner = ev_battery_passport.ownerOf(token_id)
        owner_name = get_owner_name(current_owner)
        
        print(f"\nToken ID: {token_id}")
        print(f"Battery Type: {batteryType}")
        print(f"Battery Model: {batteryModel}")
        print(f"Product Name: {productName}")
        print(f"Manufacturing Site: {manufacturingSite}")
        print(f"Supply Chain Info: {supplyChainInfo}")
        print(f"Recycled: {'Yes' if isRecycled else 'No'}")
        print(f"Returned to Manufacturer: {'Yes' if returnedToManufacturer else 'No'}")
        print(f"Current Owner: {owner_name} ({current_owner})")
        print("-------------------------------------")

    print("=====================================")

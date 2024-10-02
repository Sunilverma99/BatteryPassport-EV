import pytest
import brownie
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts, exceptions, Wei, reverts
from web3 import Web3
from web3.exceptions import BadResponseFormat

# Fixtures
@pytest.fixture
def mock_price_feed():
    return MockPriceFeed.deploy({'from': accounts[0]})

@pytest.fixture
def government_account():
    return accounts[0]

@pytest.fixture
def manufacturer_account():
    return accounts[1]

@pytest.fixture
def consumer_account():
    return accounts[2]

@pytest.fixture
def non_government_account():
    return accounts[3]

@pytest.fixture
def supplier_account():
    return accounts[4]

@pytest.fixture
def recycler_account():
    return accounts[5]

@pytest.fixture
def ev_battery_passport(mock_price_feed, government_account):
    return EVBatteryPassportLite.deploy(government_account, mock_price_feed.address, {'from': government_account})

# Price Feed Tests
def test_initial_price(mock_price_feed):
    """Test that the initial price is greater than zero."""
    initial_price = mock_price_feed.latestAnswer()
    assert initial_price > 0, "Initial price should be greater than zero"

def test_update_price(mock_price_feed):
    """Test updating the price in the mock price feed."""
    new_price = 2500 * 10**8
    mock_price_feed.updateAnswer(new_price)
    updated_price = mock_price_feed.latestAnswer()
    assert updated_price == new_price, "Updated price should match the new price"

# Deployment Tests
def test_deploy_passport(ev_battery_passport, government_account, mock_price_feed):
    """Test correct deployment of the EV Battery Passport contract."""
    assert ev_battery_passport.hasRole(ev_battery_passport.GOVERNMENT_ROLE(), government_account)
    assert ev_battery_passport.priceFeed() == mock_price_feed.address

# Deposit Tests
def test_min_deposit(ev_battery_passport):
    """Test that the minimum deposit is greater than zero."""
    min_deposit = ev_battery_passport.calculateMinDeposit()
    assert min_deposit > 0, "Minimum deposit should be greater than zero"

def test_lock_deposit(ev_battery_passport, manufacturer_account, government_account):
    """Test locking a deposit for a manufacturer."""
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': 1e18})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == 0

# Manufacturer Management Tests
def test_add_manufacturer(ev_battery_passport, government_account, manufacturer_account, non_government_account):
    """Test adding a manufacturer and verify role assignment."""
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    
    with pytest.raises((exceptions.VirtualMachineError, exceptions.TransactionError, BadResponseFormat)):
        ev_battery_passport.addManufacturer(non_government_account, {'from': non_government_account})
    
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), non_government_account)

def test_remove_manufacturer(ev_battery_passport, government_account, manufacturer_account):
    """Test removing a manufacturer."""
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.removeManufacturer(manufacturer_account, {'from': government_account})
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)

def test_duplicate_manufacturer_registration(ev_battery_passport, government_account, manufacturer_account):
    """Test that duplicate manufacturer registration doesn't change the role."""
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    initial_role = ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account) == initial_role

def test_multiple_manufacturers(ev_battery_passport, government_account):
    """Test adding multiple manufacturers and verifying their deposits and roles."""
    manufacturers = accounts[1:4]
    
    for manufacturer in manufacturers:
        ev_battery_passport.addManufacturer(manufacturer, {'from': government_account})
        ev_battery_passport.deposit({'from': manufacturer, 'value': Wei("1 ether")})
    
    for manufacturer in manufacturers:
        assert ev_battery_passport.manufacturerDeposits(manufacturer) == Wei("1 ether")
        assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer)

# Penalty Tests
def test_deposit_and_penalize(ev_battery_passport, government_account, manufacturer_account):
    """Test depositing funds and penalizing a manufacturer."""
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    
    initial_balance = manufacturer_account.balance()
    deposit_amount = Wei("2 ether")
    
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': deposit_amount})
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == deposit_amount
    
    penalty_amount = Wei("0.5 ether")
    ev_battery_passport.penalizeNonCompliance(manufacturer_account, penalty_amount, {"from": government_account})
    
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == deposit_amount - penalty_amount
    assert manufacturer_account.balance() == initial_balance - deposit_amount

def test_government_penalize_manufacturer(ev_battery_passport, government_account, manufacturer_account):
    """Test government penalizing a manufacturer."""
    ev_battery_passport.addManufacturer(manufacturer_account, {"from": government_account})
    ev_battery_passport.deposit({"from": manufacturer_account, "value": "2 ether"})
    
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == 2 * 10**18
    
    penalty_amount = 0.5 * 10**18
    ev_battery_passport.penalizeNonCompliance(manufacturer_account, penalty_amount, {"from": government_account})
    
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == 1.5 * 10**18

# Battery Management Tests
# def test_view_invalid_battery_id(ev_battery_passport, consumer_account):
#     """Test viewing an invalid battery ID."""
#     with pytest.raises(exceptions.VirtualMachineError):
#         ev_battery_passport.viewBatteryDetails(9999, {'from': consumer_account})

# def test_view_battery_details(ev_battery_passport, government_account, manufacturer_account, consumer_account):
#     """Test setting and viewing battery details."""
#     battery_id = 1
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
#     ev_battery_passport.deposit({'from': manufacturer_account, 'value': 1e18})
#     ev_battery_passport.lockDeposit({'from': manufacturer_account})

#     ev_battery_passport.setBatteryData(
#         battery_id,
#         "Model X",
#         "Location A",
#         "Lithium-Ion",
#         "Electric Battery",
#         {'from': manufacturer_account}
#     )

#     ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

#     batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer = ev_battery_passport.viewBatteryDetails(battery_id, {'from': consumer_account})

#     assert batteryType == 'Lithium-Ion'
#     assert batteryModel == 'Model X'
#     assert productName == 'Electric Battery'
#     assert manufacturingSite == 'Location A'
#     assert supplyChainInfo == ''
#     assert isRecycled == False
#     assert returnedToManufacturer == False

# Role Management Tests

# def test_role_revocation(ev_battery_passport, government_account, manufacturer_account):
#     """Test revoking a manufacturer's role and ensuring they can't perform actions."""
#     # Add the manufacturer role
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    
#     # Check that the manufacturer has the role
#     assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)

#     # Revoke the manufacturer's role
#     ev_battery_passport.revokeRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account, {'from': government_account})

#     # Check that the manufacturer no longer has the role
#     assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    
#     # Ensure an error is raised when trying to set battery data after revocation
#     with pytest.raises(exceptions.VirtualMachineError) as exc_info:
#         ev_battery_passport.setBatteryData(1, "Model X", "Location A", "Lithium-Ion", "Electric Battery", {'from': manufacturer_account})
    
#     # Check the error message for specific revert reasons
#     assert "revert" in str(exc_info.value).lower() and "missing role" in str(exc_info.value).lower()

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

    # Manufacturer sets battery data and mints token 1
    token_id_1 = 1
    off_chain_data_hash_1 = "QmYdCcEPr8R8Cp8XdEB5CP1EANg91B7cSTQk3Su6ZNnZEq"  # Example IPFS hash
    print(f"Setting battery data for token {token_id_1}...")
    tx = ev_battery_passport.setBatteryData(
        token_id_1,
        "Model Y",
        "Location B",
        "NiMH",
        "Hybrid Battery",
        off_chain_data_hash_1,  # Added offChainDataHash argument
        {'from': manufacturer_account}
    )
    print(f"Battery data set for token {token_id_1} and token minted.")

    # Test minting (setBatteryData implicitly mints a token)
    assert ev_battery_passport.ownerOf(token_id_1) == manufacturer_account
    print(f"Token {token_id_1} is owned by {manufacturer_account}.")

    # Verify BatteryDataSet event
    assert 'BatteryDataSet' in tx.events
    assert tx.events['BatteryDataSet']['tokenId'] == token_id_1
    print(f"Verified BatteryDataSet event for token {token_id_1}.")

    # Manufacturer transfers battery to supplier
    print(f"Transferring token {token_id_1} from manufacturer {manufacturer_account} to supplier {supplier_account}...")
    ev_battery_passport.transferFrom(manufacturer_account, supplier_account, token_id_1, {'from': manufacturer_account})
    assert ev_battery_passport.ownerOf(token_id_1) == supplier_account
    print(f"Token {token_id_1} successfully transferred to supplier {supplier_account}.")

    # Supplier updates supply chain info
    print("Granting supplier role and updating supply chain info...")
    ev_battery_passport.grantRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
    supply_chain_data_1 = "Shipped from Factory B to Distribution Center C"
    tx = ev_battery_passport.updateSupplyChainInfo(token_id_1, supply_chain_data_1, {'from': supplier_account})

    # Verify SupplyChainInfoUpdated event
    assert 'SupplyChainInfoUpdated' in tx.events
    print(f"Supply chain info updated for token {token_id_1} by supplier {supplier_account}.")

    # Supplier transfers battery to consumer
    print(f"Transferring token {token_id_1} from supplier {supplier_account} to consumer {consumer_account}...")
    ev_battery_passport.transferFrom(supplier_account, consumer_account, token_id_1, {'from': supplier_account})
    assert ev_battery_passport.ownerOf(token_id_1) == consumer_account
    print(f"Token {token_id_1} successfully transferred to consumer {consumer_account}.")

    # Consumer views battery details
    print("Granting consumer role and verifying battery details...")
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

    # Ensure viewBatteryDetails function can be called
    batteryDetails_1 = ev_battery_passport.viewBatteryDetails(token_id_1, {'from': consumer_account})

    # Update this line to expect 8 return values
    assert len(batteryDetails_1) == 8, "Expected 8 return values from viewBatteryDetails"

    # Unpack all 8 return values
    batteryType_1, batteryModel_1, productName_1, manufacturingSite_1, supplyChainInfo_1, isRecycled_1, returnedToManufacturer_1, offChainDataHash_1 = batteryDetails_1

    assert batteryType_1 == "NiMH"
    assert batteryModel_1 == "Model Y"
    assert productName_1 == "Hybrid Battery"
    assert manufacturingSite_1 == "Location B"
    assert supplyChainInfo_1 == "Shipped from Factory B to Distribution Center C"
    assert isRecycled_1 == False

    # Print out values obtained from viewBatteryDetails
    print("=== Battery 1 Details ===")
    print(f"Battery Type: {batteryType_1}")
    print(f"Battery Model: {batteryModel_1}")
    print(f"Product Name: {productName_1}")
    print(f"Manufacturing Site: {manufacturingSite_1}")
    print(f"Supply Chain Info: {supplyChainInfo_1}")
    print(f"Recycled: {'Yes' if isRecycled_1 else 'No'}")
    print(f"Returned to Manufacturer: {'Yes' if returnedToManufacturer_1 else 'No'}")
    print(f"Off-Chain Data Hash: {offChainDataHash_1}")

    # Consumer transfers battery to recycler
    print(f"Transferring token {token_id_1} from consumer {consumer_account} to recycler {recycler_account}...")
    ev_battery_passport.transferFrom(consumer_account, recycler_account, token_id_1, {'from': consumer_account})
    assert ev_battery_passport.ownerOf(token_id_1) == recycler_account
    print(f"Token {token_id_1} successfully transferred to recycler {recycler_account}.")

    # Recycler marks battery as recycled
    print("Granting recycler role and marking the battery as recycled...")
    ev_battery_passport.grantRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account, {'from': government_account})
    ev_battery_passport.markBatteryRecycled(token_id_1, {'from': recycler_account})

    # Verify the battery is marked as recycled
    print("Verifying recycler can view battery details...")
    assert ev_battery_passport.hasRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account), "Recycler doesn't have the RECYCLER_ROLE"

    # Grant additional roles if necessary (e.g., if CONSUMER_ROLE is required to view details)
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), recycler_account, {'from': government_account})
    
    # Now the recycler can view battery details
    batteryDetails_recycler = ev_battery_passport.viewBatteryDetails(token_id_1, {'from': recycler_account})
    assert len(batteryDetails_recycler) == 8, "Expected 8 return values from viewBatteryDetails"

    # Unpack all 8 return values
    batteryType_r, batteryModel_r, productName_r, manufacturingSite_r, supplyChainInfo_r, isRecycled_r, returnedToManufacturer_r, offChainDataHash_r = batteryDetails_recycler

    assert batteryType_r == "NiMH"
    assert batteryModel_r == "Model Y"
    assert productName_r == "Hybrid Battery"
    assert manufacturingSite_r == "Location B"
    assert supplyChainInfo_r == "Shipped from Factory B to Distribution Center C"
    assert isRecycled_r == True
    print(f"Verified battery details for token {token_id_1} after marking as recycled.")

    # Additional check: Verify that the government account can also view the details
    print("Verifying government can view battery details...")
    govBatteryDetails = ev_battery_passport.viewBatteryDetails(token_id_1, {'from': government_account})
    assert len(govBatteryDetails) == 8, "Expected 8 return values from viewBatteryDetails"

    # Unpack all 8 return values
    govBatteryType, _, _, _, _, govIsRecycled, _, govOffChainDataHash = govBatteryDetails
    assert govBatteryType == "NiMH"
    assert govIsRecycled == True
    print("Government successfully viewed battery details.")

    print("ERC721 functionality test for token 1 completed successfully.")
    
    # Create a second token with different data
    token_id_2 = 2
    off_chain_data_hash_2 = "QmYdCcEPr8R8Cp8XdEB5CP1EANg91B7cSTQk3Su6ZNnZEq"  # Example IPFS hash for second token
    print(f"Setting battery data for second token {token_id_2}...")
    tx_2 = ev_battery_passport.setBatteryData(
        token_id_2,
        "Model X",
        "Location A",
        "Li-ion",
        "Electric Battery",
        off_chain_data_hash_2,  # Added offChainDataHash argument
        {'from': manufacturer_account}
    )
    print(f"Battery data set for token {token_id_2} and token minted.")

    # Test minting (setBatteryData implicitly mints a token)
    assert ev_battery_passport.ownerOf(token_id_2) == manufacturer_account
    print(f"Token {token_id_2} is owned by {manufacturer_account}.")

    # Verify BatteryDataSet event for second token
    assert 'BatteryDataSet' in tx_2.events
    assert tx_2.events['BatteryDataSet']['tokenId'] == token_id_2
    print(f"Verified BatteryDataSet event for token {token_id_2}.")

    # Transfer token 2 to supplier
    print(f"Transferring token {token_id_2} from manufacturer {manufacturer_account} to supplier {supplier_account}...")
    ev_battery_passport.transferFrom(manufacturer_account, supplier_account, token_id_2, {'from': manufacturer_account})
    assert ev_battery_passport.ownerOf(token_id_2) == supplier_account
    print(f"Token {token_id_2} successfully transferred to supplier {supplier_account}.")

    # Supplier updates supply chain info for second token
    print("Updating supply chain info for second token...")
    supply_chain_data_2 = "Shipped from Factory A to Distribution Center B"
    tx_2_supply_chain = ev_battery_passport.updateSupplyChainInfo(token_id_2, supply_chain_data_2, {'from': supplier_account})

    # Verify SupplyChainInfoUpdated event
    assert 'SupplyChainInfoUpdated' in tx_2_supply_chain.events
    print(f"Supply chain info updated for token {token_id_2} by supplier {supplier_account}.")

    # Supplier transfers token 2 to consumer
    print(f"Transferring token {token_id_2} from supplier {supplier_account} to consumer {consumer_account}...")
    ev_battery_passport.transferFrom(supplier_account, consumer_account, token_id_2, {'from': supplier_account})
    assert ev_battery_passport.ownerOf(token_id_2) == consumer_account
    print(f"Token {token_id_2} successfully transferred to consumer {consumer_account}.")

    # Consumer views details of second token
    print("Consumer viewing details of second token...")
    batteryDetails_2 = ev_battery_passport.viewBatteryDetails(token_id_2, {'from': consumer_account})

    # Update this line to expect 8 return values for the second token
    assert len(batteryDetails_2) == 8, "Expected 8 return values from viewBatteryDetails"

    # Unpack all 8 return values
    batteryType_2, batteryModel_2, productName_2, manufacturingSite_2, supplyChainInfo_2, isRecycled_2, returnedToManufacturer_2, offChainDataHash_2 = batteryDetails_2

    assert batteryType_2 == "Li-ion"
    assert batteryModel_2 == "Model X"
    assert productName_2 == "Electric Battery"
    assert manufacturingSite_2 == "Location A"
    assert supplyChainInfo_2 == "Shipped from Factory A to Distribution Center B"
    assert isRecycled_2 == False

    # Print out values obtained from viewBatteryDetails for second token
    print("=== Battery 2 Details ===")
    print(f"Battery Type: {batteryType_2}")
    print(f"Battery Model: {batteryModel_2}")
    print(f"Product Name: {productName_2}")
    print(f"Manufacturing Site: {manufacturingSite_2}")
    print(f"Supply Chain Info: {supplyChainInfo_2}")
    print(f"Recycled: {'Yes' if isRecycled_2 else 'No'}")
    print(f"Returned to Manufacturer: {'Yes' if returnedToManufacturer_2 else 'No'}")
    print(f"Off-Chain Data Hash: {offChainDataHash_2}")

    print("=== ERC721 Functionality Test Completed Successfully ===")

    
# Role Management Tests
# def test_role_revocation(ev_battery_passport, government_account, manufacturer_account):
#     """Test revoking a manufacturer's role and ensuring they can't perform actions."""
#     # Add the manufacturer role
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    
#     # Check that the manufacturer has the role
#     assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)

#     # Revoke the manufacturer's role
#     ev_battery_passport.revokeRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account, {'from': government_account})

#     # Check that the manufacturer no longer has the role
#     assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    
#     # Ensure an error is raised when trying to set battery data after revocation
#     with pytest.raises(exceptions.VirtualMachineError):
#         ev_battery_passport.setBatteryData(1, "Model X", "Location A", "Lithium-Ion", "Electric Battery", {'from': manufacturer_account})

# Access Control Tests
def test_add_supplier(ev_battery_passport, government_account, supplier_account):
    """Test adding a supplier role."""
    ev_battery_passport.grantRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
    assert ev_battery_passport.hasRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account)
    print(f"Supplier role granted to {supplier_account}.")

def test_remove_supplier(ev_battery_passport, government_account, supplier_account):
    """Test removing a supplier role."""
    ev_battery_passport.grantRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
    ev_battery_passport.revokeRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
    assert not ev_battery_passport.hasRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account)
    print(f"Supplier role revoked from {supplier_account}.")

def test_add_recycler(ev_battery_passport, government_account, recycler_account):
    """Test adding a recycler role."""
    ev_battery_passport.grantRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account, {'from': government_account})
    assert ev_battery_passport.hasRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account)
    print(f"Recycler role granted to {recycler_account}.")

def test_remove_recycler(ev_battery_passport, government_account, recycler_account):
    """Test removing a recycler role."""
    ev_battery_passport.grantRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account, {'from': government_account})
    ev_battery_passport.revokeRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account, {'from': government_account})
    assert not ev_battery_passport.hasRole(ev_battery_passport.RECYCLER_ROLE(), recycler_account)
    print(f"Recycler role revoked from {recycler_account}.")

def test_add_consumer(ev_battery_passport, government_account, consumer_account):
    """Test adding a consumer role."""
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})
    assert ev_battery_passport.hasRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account)
    print(f"Consumer role granted to {consumer_account}.")

def test_remove_consumer(ev_battery_passport, government_account, consumer_account):
    """Test removing a consumer role."""
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})
    ev_battery_passport.revokeRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})
    assert not ev_battery_passport.hasRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account)
    print(f"Consumer role revoked from {consumer_account}.")

# Supplier Functionality Tests
# def test_update_supply_chain_info(ev_battery_passport, government_account, manufacturer_account, supplier_account):
#     """Test updating supply chain information by a supplier."""
#     # Setup
#     token_id = 1
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
#     ev_battery_passport.deposit({'from': manufacturer_account, 'value': Wei("1 ether")})
#     ev_battery_passport.lockDeposit({'from': manufacturer_account})
#     ev_battery_passport.setBatteryData(
#         token_id,
#         "Model X",
#         "Location A",
#         "Lithium-Ion",
#         "Electric Battery",
#         {'from': manufacturer_account}
#     )

#     # Add supplier role
#     ev_battery_passport.grantRole(ev_battery_passport.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
    
#     # Grant CONSUMER_ROLE to supplier for viewing details (this is a workaround for testing)
#     ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), supplier_account, {'from': government_account})

#     # Update supply chain info
#     supply_chain_data = "Shipped from Factory A to Distribution Center B"
#     tx = ev_battery_passport.updateSupplyChainInfo(token_id, supply_chain_data, {'from': supplier_account})

#     # Verify event
#     assert 'SupplyChainInfoUpdated' in tx.events
#     assert tx.events['SupplyChainInfoUpdated']['tokenId'] == token_id
#     assert tx.events['SupplyChainInfoUpdated']['supplier'] == supplier_account
#     assert tx.events['SupplyChainInfoUpdated']['supplyChainData'] == supply_chain_data

#     # Verify updated data
#     _, _, _, _, updated_supply_chain_info, _, _ = ev_battery_passport.viewBatteryDetails(token_id, {'from': supplier_account})
#     assert updated_supply_chain_info == supply_chain_data
#     print(f"Supply chain info updated successfully for token {token_id}.")
    
# def test_unauthorized_supplier_update(ev_battery_passport, government_account, manufacturer_account, consumer_account):
#     """Test that unauthorized accounts cannot update supply chain info."""
#     # Setup
#     token_id = 1
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
#     ev_battery_passport.deposit({'from': manufacturer_account, 'value': Wei("1 ether")})
#     ev_battery_passport.lockDeposit({'from': manufacturer_account})
#     ev_battery_passport.setBatteryData(
#         token_id,
#         "Model X",
#         "Location A",
#         "Lithium-Ion",
#         "Electric Battery",
#         {'from': manufacturer_account}
#     )

#     # Attempt to update supply chain info with unauthorized account
#     with pytest.raises(Exception) as excinfo:
#         ev_battery_passport.updateSupplyChainInfo(token_id, "Unauthorized update", {'from': consumer_account})
    
#     # Check if the error message contains the expected content
#     assert "AccessControl" in str(excinfo.value)
#     assert "missing role" in str(excinfo.value)
#     print("Unauthorized update attempt correctly reverted.")
    

# Consent Management Tests

# def test_consent_management(
#     ev_battery_passport,
#     government_account,
#     manufacturer_account,
#     consumer_account,
#     non_government_account,
#     supplier_account
# ):
#     # Set up: Add manufacturer and mint a battery
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
#     ev_battery_passport.deposit({'from': manufacturer_account, 'value': Web3.toWei(1, "ether")})
#     ev_battery_passport.lockDeposit({'from': manufacturer_account})
    
#     battery_id = 1
#     ev_battery_passport.setBatteryData(
#         battery_id,
#         "Model X",
#         "Location A",
#         "Lithium-Ion",
#         "Electric Battery",
#         {'from': manufacturer_account}
#     )

#     # Grant consumer role
#     ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

#     # Test initial consent status
#     assert ev_battery_passport.checkConsent(battery_id, supplier_account) == False, "Initial consent should be false"

#     # Test granting consent
#     ev_battery_passport.grantConsent(battery_id, supplier_account, {'from': consumer_account})
#     assert ev_battery_passport.checkConsent(battery_id, supplier_account) == True, "Consent should be granted"

#     # Test revoking consent
#     ev_battery_passport.revokeConsent(battery_id, supplier_account, {'from': consumer_account})
#     assert ev_battery_passport.checkConsent(battery_id, supplier_account) == False, "Consent should be revoked"

#     # Test granting consent for non-existent token
#     with reverts("ERC721: token does not exist"):
#         ev_battery_passport.grantConsent(999, supplier_account, {'from': consumer_account})

#     # Test granting consent from non-consumer account
#     consumer_role = ev_battery_passport.CONSUMER_ROLE()
#     with reverts(f"AccessControl: account {non_government_account.address.lower()} is missing role {consumer_role}"):
#         ev_battery_passport.grantConsent(battery_id, supplier_account, {'from': non_government_account})

#     # Test revoking consent for non-existent token
#     with reverts("ERC721: token does not exist"):
#         ev_battery_passport.revokeConsent(999, supplier_account, {'from': consumer_account})

#     # Test revoking consent from non-consumer account
#     with reverts(f"AccessControl: account {non_government_account.address.lower()} is missing role {consumer_role}"):
#         ev_battery_passport.revokeConsent(battery_id, supplier_account, {'from': non_government_account})

#     print("All consent management tests passed successfully!")
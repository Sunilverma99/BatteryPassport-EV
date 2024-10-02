import pytest
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts, exceptions, Wei
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
def test_view_invalid_battery_id(ev_battery_passport, consumer_account):
    """Test viewing an invalid battery ID."""
    with pytest.raises(exceptions.VirtualMachineError):
        ev_battery_passport.viewBatteryDetails(9999, {'from': consumer_account})

def test_view_battery_details(ev_battery_passport, government_account, manufacturer_account, consumer_account):
    """Test setting and viewing battery details."""
    battery_id = 1
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': 1e18})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})

    ev_battery_passport.setBatteryData(
        battery_id,
        "Model X",
        "Location A",
        "Lithium-Ion",
        "Electric Battery",
        {'from': manufacturer_account}
    )

    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(battery_id, {'from': consumer_account})

    assert batteryType == 'Lithium-Ion'
    assert batteryModel == 'Model X'
    assert productName == 'Electric Battery'
    assert manufacturingSite == 'Location A'

# Role Management Tests
def test_role_revocation(ev_battery_passport, government_account, manufacturer_account):
    """Test revoking a manufacturer's role and ensuring they can't perform actions."""
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    
    ev_battery_passport.revokeRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account, {'from': government_account})
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)
    
    with pytest.raises((exceptions.VirtualMachineError, BadResponseFormat)) as exc_info:
        ev_battery_passport.setBatteryData(1, "Model X", "Location A", "Lithium-Ion", "Electric Battery", {'from': manufacturer_account})
    
    error_message = str(exc_info.value)
    assert "revert" in error_message.lower() and "missing role" in error_message.lower()
    
def test_erc721_functionality(ev_battery_passport, government_account, manufacturer_account, consumer_account):
    """Test basic ERC721 functionality and battery data setting."""
    # Add manufacturer and set up deposit
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': Wei("1 ether")})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})

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

    # Test minting (setBatteryData implicitly mints a token)
    assert ev_battery_passport.ownerOf(token_id) == manufacturer_account

    # Verify BatteryDataSet event
    assert 'BatteryDataSet' in tx.events
    assert tx.events['BatteryDataSet']['tokenId'] == token_id
    assert tx.events['BatteryDataSet']['manufacturer'] == manufacturer_account
    assert tx.events['BatteryDataSet']['batteryModel'] == "Model Y"
    assert tx.events['BatteryDataSet']['batteryType'] == "NiMH"
    assert tx.events['BatteryDataSet']['productName'] == "Hybrid Battery"

    # Test transferring
    ev_battery_passport.transferFrom(manufacturer_account, consumer_account, token_id, {'from': manufacturer_account})
    assert ev_battery_passport.ownerOf(token_id) == consumer_account

    # Verify battery data
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})
    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(token_id, {'from': consumer_account})
    assert batteryType == "NiMH"
    assert batteryModel == "Model Y"
    assert productName == "Hybrid Battery"
    assert manufacturingSite == "Location B"

    # Test minting a token with a different ID (should succeed)
    new_token_id = 2  # Different token ID
    tx = ev_battery_passport.setBatteryData(
        new_token_id,
        "Model Z",
        "Location C",
        "Li-ion",
        "Electric Car Battery",
        {'from': manufacturer_account}
    )
    assert ev_battery_passport.ownerOf(new_token_id) == manufacturer_account

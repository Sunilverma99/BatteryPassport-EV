import pytest
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts, exceptions

from web3 import Web3
from web3.exceptions import BadResponseFormat

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
    return accounts[2]  # New consumer account for testing

@pytest.fixture
def non_government_account():
    return accounts[3]

@pytest.fixture
def ev_battery_passport(mock_price_feed, government_account):
    return EVBatteryPassportLite.deploy(government_account, mock_price_feed.address, {'from': government_account})

# Test for initial price
def test_initial_price(mock_price_feed):
    initial_price = mock_price_feed.latestAnswer()
    assert initial_price > 0, "Initial price should be greater than zero"

# Test for updating price
def test_update_price(mock_price_feed):
    new_price = 2500 * 10**8
    mock_price_feed.updateAnswer(new_price)
    updated_price = mock_price_feed.latestAnswer()
    assert updated_price == new_price, "Updated price should match the new price"

# Test for deploying the passport
def test_deploy_passport(ev_battery_passport, government_account, mock_price_feed):
    assert ev_battery_passport.hasRole(ev_battery_passport.GOVERNMENT_ROLE(), government_account)
    assert ev_battery_passport.priceFeed() == mock_price_feed.address

# Test for minimum deposit
def test_min_deposit(ev_battery_passport):
    min_deposit = ev_battery_passport.calculateMinDeposit()
    assert min_deposit > 0, "Minimum deposit should be greater than zero"

# Test for locking the deposit
def test_lock_deposit(ev_battery_passport, manufacturer_account, government_account):
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': 1e18})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == 0
    
    # Test for adding a manufacturer
def test_add_manufacturer(ev_battery_passport, government_account, manufacturer_account, non_government_account):
    # Ensure that initially, the manufacturer doesn't have the MANUFACTURER_ROLE
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)

    # Add the manufacturer using the government account
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})

    # Verify that the manufacturer now has the MANUFACTURER_ROLE
    assert ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)

    # Try to add a manufacturer using a non-government account and expect it to fail
    try:
        ev_battery_passport.addManufacturer(non_government_account, {'from': non_government_account})
    except (exceptions.VirtualMachineError, exceptions.TransactionError, BadResponseFormat) as e:
        # Check if the error message contains the expected revert reason
        assert "revert" in str(e)
    else:
        pytest.fail("Transaction did not revert as expected")

    # Verify that the non-government account still does not have the MANUFACTURER_ROLE
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), non_government_account)
    
# Test for removing a manufacturer
def test_remove_manufacturer(ev_battery_passport, government_account, manufacturer_account):
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.removeManufacturer(manufacturer_account, {'from': government_account})
    assert not ev_battery_passport.hasRole(ev_battery_passport.MANUFACTURER_ROLE(), manufacturer_account)

# Corrected test for government penalizing manufacturer
def test_government_penalize_manufacturer(ev_battery_passport, government_account, manufacturer_account):
    # Add manufacturer
    ev_battery_passport.addManufacturer(manufacturer_account, {"from": government_account})

    # Deposit funds by manufacturer
    ev_battery_passport.deposit({"from": manufacturer_account, "value": "2 ether"})

    # Check deposit
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == 2 * 10**18  # 2 ether in wei

    # Penalize manufacturer
    penalty_amount = 0.5 * 10**18  # 0.5 ether in wei
    ev_battery_passport.penalizeNonCompliance(manufacturer_account, penalty_amount, {"from": government_account})

    # Check reduced deposit
    assert ev_battery_passport.manufacturerDeposits(manufacturer_account) == 1.5 * 10**18  # 1.5 ether in wei

# New test for viewing battery details
def test_view_battery_details(ev_battery_passport, government_account, manufacturer_account, consumer_account):
    # Set up a battery and assign it to a tokenId
    battery_id = 1
    ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
    ev_battery_passport.deposit({'from': manufacturer_account, 'value': 1e18})
    ev_battery_passport.lockDeposit({'from': manufacturer_account})

    # Assign battery data
    ev_battery_passport.setBatteryData(
        battery_id,
        "Model X",          # batteryModel
        "Location A",       # manufacturerLocation
        "Lithium-Ion",      # batteryType
        "Electric Battery", # productName
        {'from': manufacturer_account}
    )

    # Grant CONSUMER_ROLE to consumer_account
    ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

    # Now view the battery details
    batteryType, batteryModel, productName, manufacturingSite = ev_battery_passport.viewBatteryDetails(battery_id, {'from': consumer_account})

    assert batteryType == 'Lithium-Ion'
    assert batteryModel == 'Model X'
    assert productName == 'Electric Battery'
    assert manufacturingSite == 'Location A'

# tests/conftest.py

import pytest
from brownie import MockPriceFeed, EVBatteryPassportLite, accounts

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

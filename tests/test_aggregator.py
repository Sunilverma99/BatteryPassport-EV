import pytest
from brownie import MockPriceFeed, accounts

@pytest.fixture
def mock_price_feed():
    # Deploy the mock aggregator
    mock_price_feed = MockPriceFeed.deploy({'from': accounts[0]})
    return mock_price_feed

def test_initial_price(mock_price_feed):
    # Check the initial price
    initial_price = mock_price_feed.latestAnswer()
    print(f"Initial price: {initial_price}")
    assert initial_price > 0, "Initial price should be greater than zero"

def test_update_price(mock_price_feed):
    # Update the price using updateAnswer method
    new_price = 2500 * 10**8  # New price
    mock_price_feed.updateAnswer(new_price)  # Call the appropriate method to update the price
    
    updated_price = mock_price_feed.latestAnswer()
    print(f"Updated price: {updated_price}")
    assert updated_price == new_price, "Updated price should match the new price"

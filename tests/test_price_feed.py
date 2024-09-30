# tests/test_price_feed.py

import pytest

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

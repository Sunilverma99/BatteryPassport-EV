# tests/test_deployment.py

import pytest

def test_deploy_passport(ev_battery_passport, government_account, mock_price_feed):
    """Test correct deployment of the EV Battery Passport contract."""
    assert ev_battery_passport.hasRole(ev_battery_passport.GOVERNMENT_ROLE(), government_account)
    assert ev_battery_passport.priceFeed() == mock_price_feed.address

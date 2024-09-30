# tests/test_deposit.py

import pytest

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

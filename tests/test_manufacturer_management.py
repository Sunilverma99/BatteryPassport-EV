# tests/test_manufacturer_management.py

import pytest
from brownie import exceptions
from web3.exceptions import BadResponseFormat

# tests/test_manufacturer_management.py
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

# tests/test_role_management.py

import pytest
from brownie import exceptions
from web3.exceptions import BadResponseFormat

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
    

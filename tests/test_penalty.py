# tests/test_penalty.py

import pytest
from brownie import Wei, exceptions

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

# tests/test_battery_management.py

import pytest
from brownie import exceptions

# def test_view_invalid_battery_id(ev_battery_passport, consumer_account):
#     """Test viewing an invalid battery ID."""
#     with pytest.raises(exceptions.VirtualMachineError):
#         ev_battery_passport.viewBatteryDetails(9999, {'from': consumer_account})

# def test_view_battery_details(ev_battery_passport, government_account, manufacturer_account, consumer_account):
#     """Test setting and viewing battery details."""
#     battery_id = 1
#     ev_battery_passport.addManufacturer(manufacturer_account, {'from': government_account})
#     ev_battery_passport.deposit({'from': manufacturer_account, 'value': 1e18})
#     ev_battery_passport.lockDeposit({'from': manufacturer_account})

#     ev_battery_passport.setBatteryData(
#         battery_id,
#         "Model X",
#         "Location A",
#         "Lithium-Ion",
#         "Electric Battery",
#         {'from': manufacturer_account}
#     )

#     ev_battery_passport.grantRole(ev_battery_passport.CONSUMER_ROLE(), consumer_account, {'from': government_account})

#     batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer = ev_battery_passport.viewBatteryDetails(battery_id, {'from': consumer_account})

#     assert batteryType == 'Lithium-Ion'
#     assert batteryModel == 'Model X'
#     assert productName == 'Electric Battery'
#     assert manufacturingSite == 'Location A'
#     assert supplyChainInfo == ''
#     assert isRecycled == False
#     assert returnedToManufacturer == False
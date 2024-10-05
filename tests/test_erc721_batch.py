import pytest
from brownie import MockPriceFeed, EVBatteryPassportBatch, EVBatteryPassportLite, accounts, exceptions, Wei
from web3 import Web3
import requests

@pytest.fixture
def government_account():
    return accounts[0]

@pytest.fixture
def manufacturer_account():
    return accounts[1]

@pytest.fixture
def supplier_account():
    return accounts[2]

@pytest.fixture
def consumer_account():
    return accounts[3]

@pytest.fixture
def recycler_account():
    return accounts[4]

@pytest.fixture
def ev_battery_passport_batch(MockPriceFeed, EVBatteryPassportLite, accounts):
    price_feed = MockPriceFeed.deploy({'from': accounts[0]})
    return EVBatteryPassportLite.deploy(accounts[0], price_feed.address, {'from': accounts[0]})

def retrieve_off_chain_data(ipfs_hash):
    """Function to retrieve data from IPFS using the IPFS hash."""
    ipfs_gateway_url = f"https://ipfs.io/ipfs/{ipfs_hash}"  # IPFS gateway URL
    try:
        response = requests.get(ipfs_gateway_url)
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()  # Assuming off-chain data is stored as JSON
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve IPFS data: {e}")
        return None

def test_erc721_batch_functionality(ev_battery_passport_batch, government_account, manufacturer_account, supplier_account, recycler_account, consumer_account):
    """Test ERC721 batch minting functionality from manufacturer to multiple tokens and viewing their details."""

    print("Adding manufacturer and setting up deposit...")
    ev_battery_passport_batch.addManufacturer(manufacturer_account, {'from': government_account})

    # Get the minimum deposit required in Wei
    min_deposit_in_wei = ev_battery_passport_batch.calculateMinDeposit({'from': government_account})
    print(f"Minimum deposit required is {min_deposit_in_wei} Wei.")

    # Manufacturer deposits the minimum required amount
    print(f"Manufacturer locking deposit of {min_deposit_in_wei} Wei...")
    ev_battery_passport_batch.deposit({'from': manufacturer_account, 'value': min_deposit_in_wei})
    ev_battery_passport_batch.lockDeposit({'from': manufacturer_account})
    print(f"Manufacturer {manufacturer_account} added and deposit locked.")

    # Prepare batch data for minting
    token_ids = [1, 2, 3]  # Example token IDs
    battery_models = ["Tesla 4680", "LG Chem 21700", "Panasonic NCR18650B"]
    manufacturer_locations = ["Austin, Texas, USA", "Seongnam, South Korea", "Osaka, Japan"]
    battery_types = ["Lithium-ion", "Lithium-ion", "Lithium-ion"]
    product_names = ["Tesla Battery Pack", "LG Chem Electric Vehicle Battery", "Panasonic Electric Vehicle Battery"]
    off_chain_data_hashes = [
    "QmPoEfuyhqEY7YZAmMmEoGc5Kco59EQ8kBQHfv6Q5a4CwQ",  # IPFS hash for Tesla
    "QmPoEfuyhqEY7YZAmMmEoGc5Kco59EQ8kBQHfv6Q5a4CwQ",  # IPFS hash for LG Chem
    "QmPoEfuyhqEY7YZAmMmEoGc5Kco59EQ8kBQHfv6Q5a4CwQ"   # IPFS hash for Panasonic
]

    # Mint batteries in batch
    print("Minting batch of battery tokens...")
    tx = ev_battery_passport_batch.mintBatteryBatch(
        token_ids,
        battery_models,
        manufacturer_locations,
        battery_types,
        product_names,
        off_chain_data_hashes,
        {'from': manufacturer_account}
    )
    print("Batch minting transaction completed.")

    # Verify that each token was minted and events were emitted
    for i, token_id in enumerate(token_ids):
        assert ev_battery_passport_batch.ownerOf(token_id) == manufacturer_account
        print(f"Token {token_id} minted and owned by {manufacturer_account}.")

        # Verify BatteryDataSet event for each token
        assert 'BatteryDataSet' in tx.events
        event = tx.events['BatteryDataSet'][i]
        assert event['tokenId'] == token_id
        assert event['manufacturer'] == manufacturer_account
        assert event['batteryModel'] == battery_models[i]
        assert event['batteryType'] == battery_types[i]
        assert event['productName'] == product_names[i]
        print(f"Verified BatteryDataSet event for token {token_id}.")

    # Now, perform operations similar to single token test for each token in batch
    for i, token_id in enumerate(token_ids):
        # Manufacturer transfers battery to supplier
        print(f"Transferring token {token_id} from manufacturer {manufacturer_account} to supplier {supplier_account}...")
        ev_battery_passport_batch.transferFrom(manufacturer_account, supplier_account, token_id, {'from': manufacturer_account})
        assert ev_battery_passport_batch.ownerOf(token_id) == supplier_account
        print(f"Token {token_id} successfully transferred to supplier {supplier_account}.")

        # Supplier updates supply chain info
        print("Granting supplier role and updating supply chain info...")
        ev_battery_passport_batch.grantRole(ev_battery_passport_batch.SUPPLIER_ROLE(), supplier_account, {'from': government_account})
        supply_chain_data = f"Shipped from Factory {chr(66 + i)} to Distribution Center {chr(67 + i)}"
        tx_supply = ev_battery_passport_batch.updateSupplyChainInfo(token_id, supply_chain_data, {'from': supplier_account})

        # Verify SupplyChainInfoUpdated event
        assert 'SupplyChainInfoUpdated' in tx_supply.events
        print(f"Supply chain info updated for token {token_id} by supplier {supplier_account}.")

        # Supplier transfers battery to consumer
        print(f"Transferring token {token_id} from supplier {supplier_account} to consumer {consumer_account}...")
        ev_battery_passport_batch.transferFrom(supplier_account, consumer_account, token_id, {'from': supplier_account})
        assert ev_battery_passport_batch.ownerOf(token_id) == consumer_account
        print(f"Token {token_id} successfully transferred to consumer {consumer_account}.")

        # Consumer views battery details
        print("Granting consumer role and verifying battery details...")
        ev_battery_passport_batch.grantRole(ev_battery_passport_batch.CONSUMER_ROLE(), consumer_account, {'from': government_account})

        # Ensure viewBatteryDetails function can be called
        batteryDetails = ev_battery_passport_batch.viewBatteryDetails(token_id, {'from': consumer_account})

        # Check for the expected number of return values
        assert len(batteryDetails) == 8, "Expected 8 return values from viewBatteryDetails"

        # Unpack all 8 return values
        batteryType, batteryModel, productName, manufacturingSite, supplyChainInfo, isRecycled, returnedToManufacturer, offChainDataHash = batteryDetails

        # Verify the details
        assert batteryType == battery_types[i]
        assert batteryModel == battery_models[i]
        assert productName == product_names[i]
        assert manufacturingSite == manufacturer_locations[i]
        assert supply_chain_data == supplyChainInfo
        assert not isRecycled
        assert not returnedToManufacturer
        assert offChainDataHash == off_chain_data_hashes[i]

        # Print out values obtained from viewBatteryDetails
        print("=== Battery Details ===")
        print(f"Battery Type: {batteryType}")
        print(f"Battery Model: {batteryModel}")
        print(f"Product Name: {productName}")
        print(f"Manufacturing Site: {manufacturingSite}")
        print(f"Supply Chain Info: {supplyChainInfo}")
        print(f"Recycled: {'Yes' if isRecycled else 'No'}")
        print(f"Returned to Manufacturer: {'Yes' if returnedToManufacturer else 'No'}")
        print(f"Off-Chain Data Hash: {offChainDataHash}")

        # Fetch and print off-chain data from IPFS 
        off_chain_data = retrieve_off_chain_data(offChainDataHash)
        if off_chain_data:
            print(f"=== Off-Chain Data for token {token_id} (from IPFS) ===")
            print(off_chain_data)
        else:
            print(f"Failed to retrieve off-chain data for token {token_id}.")

        # Consumer transfers battery to recycler
        print(f"Transferring token {token_id} from consumer {consumer_account} to recycler {recycler_account}...")
        ev_battery_passport_batch.transferFrom(consumer_account, recycler_account, token_id, {'from': consumer_account})
        assert ev_battery_passport_batch.ownerOf(token_id) == recycler_account
        print(f"Token {token_id} successfully transferred to recycler {recycler_account}.")

        # Recycler marks battery as recycled
        print("Granting recycler role and marking the battery as recycled...")
        ev_battery_passport_batch.grantRole(ev_battery_passport_batch.RECYCLER_ROLE(), recycler_account, {'from': government_account})
        ev_battery_passport_batch.markBatteryRecycled(token_id, {'from': recycler_account})

        # Verify the battery is marked as recycled
        print("Verifying recycler can view battery details...")
        
        # Check if the recycler has the correct role
        assert ev_battery_passport_batch.hasRole(ev_battery_passport_batch.RECYCLER_ROLE(), recycler_account), "Recycler doesn't have the RECYCLER_ROLE"

        # Now the recycler can view the details
        batteryDetails = ev_battery_passport_batch.viewBatteryDetails(token_id, {'from': recycler_account})

        # Check if the isRecycled flag is updated
        _, _, _, _, _, isRecycled, _, _ = batteryDetails
        assert isRecycled, "The battery should be marked as recycled by now."
        print(f"Battery {token_id} has been marked as recycled successfully.")

    print("All batch operations executed successfully!")

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

// Import necessary OpenZeppelin contracts
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

/**
 * @title EVBatteryPassportLite
 * @dev A simplified version of EVBatteryPassport to test roles and deposits.
 */
contract EVBatteryPassportLite is ERC721, AccessControl, ReentrancyGuard {
    // Role definitions using AccessControl
    bytes32 public constant GOVERNMENT_ROLE = DEFAULT_ADMIN_ROLE;
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant SUPPLIER_ROLE = keccak256("SUPPLIER_ROLE");
    bytes32 public constant RECYCLER_ROLE = keccak256("RECYCLER_ROLE");
    bytes32 public constant CONSUMER_ROLE = keccak256("CONSUMER_ROLE");

    // Chainlink price feed for GBP/ETH conversion
    AggregatorV3Interface public priceFeed;

    // Minimum deposit amount in GBP (set to £10 with 18 decimals)
    uint256 public constant MIN_DEPOSIT_GBP = 10 * 10**18;

    // Mapping to store manufacturer deposits
    mapping(address => uint256) public manufacturerDeposits;


   // Struct to store consent
    struct Consent {
    mapping(address => bool) consentStatus; // Tracks consent for each address
    }

    // Struct to store battery identification details
    struct Identification {
    string batteryModel;
    string manufacturerLocation;
    }

    // Struct to store technical specifications of the battery
    struct TechnicalSpecifications {
    string batteryType;
    }

    // Struct to store battery data
    struct BatteryData {
    Identification identification;
    TechnicalSpecifications technicalSpecifications;
    string productName;
    string supplyChainInfo;
    bool isRecycled;
    bool returnedToManufacturer;
    string offChainDataHash;  // IPFS hash for storing off-chain data
    }


    // Mapping from tokenId to BatteryData
    mapping(uint256 => BatteryData) public batteryData;

    // Mapping to store consent approvals (tokenId => Consent struct)
    mapping(uint256 => Consent) private batteryConsent;


    // Events
    event DepositLocked(address indexed manufacturer, uint256 amount, uint256 timestamp);
    event ManufacturerAdded(address indexed manufacturer, uint256 timestamp);
    event ManufacturerRemoved(address indexed manufacturer, uint256 timestamp);
    event PenaltyApplied(address indexed manufacturer, uint256 amount, uint256 timestamp);
    event BatteryDataSet(uint256 indexed tokenId, address indexed manufacturer, string batteryModel, string batteryType, string productName);
    event SupplyChainInfoUpdated(uint256 indexed tokenId, address indexed supplier, string supplyChainData);
    event BatteryRecycled(uint256 indexed tokenId, address indexed recycler);
    event BatteryReturnedToManufacturer(uint256 indexed tokenId, address indexed recycler, address indexed manufacturer);
    event ConsentGranted(uint256 indexed tokenId, address indexed role);
    event ConsentRevoked(uint256 indexed tokenId, address indexed role);

    // Custom errors for gas efficiency
    error OnlyGovernment();
    error InsufficientDeposit(uint256 required, uint256 provided);
    error OnlyManufacturer();

    /**
     * @notice Constructor to set up roles and initialize the contract.
     * @param _government The address assigned the GOVERNMENT_ROLE.
     * @param _priceFeed The address of the Chainlink price feed.
     */
    constructor(address _government, address _priceFeed)
        ERC721("EVBatteryPassportLite", "EVBPL")
    {
        // Set up roles
        _setupRole(GOVERNMENT_ROLE, _government);
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    modifier onlyGovernment() {
        if (!hasRole(GOVERNMENT_ROLE, msg.sender)) revert OnlyGovernment();
        _;
    }

    modifier onlyManufacturer() {
        require(hasRole(MANUFACTURER_ROLE, msg.sender), "Caller is not a manufacturer");
        _;
    }

    modifier onlySupplier() {
        require(hasRole(SUPPLIER_ROLE, msg.sender), "Caller is not a supplier");
        _;
    }

    modifier onlyRecycler() {
    require(hasRole(RECYCLER_ROLE, msg.sender), "Caller is not a recycler");
    _;
    }

    modifier onlyConsumer() {
        require(hasRole(CONSUMER_ROLE, msg.sender), "Caller is not a consumer");
        _;
    }



    modifier hasMinimumDeposit() {
        uint256 requiredDeposit = calculateMinDeposit();
        uint256 providedDeposit = manufacturerDeposits[msg.sender];
        if (providedDeposit < requiredDeposit) revert InsufficientDeposit(requiredDeposit, providedDeposit);
        _;
    }

    //Functions 

    // Price and Deposit Functions
    function getLatestPrice() public view returns (uint256 price) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        require(answer > 0, "Invalid price feed data");
        price = uint256(answer);
    }

    function calculateMinDeposit() public view returns (uint256 minDepositInWei) {
        uint256 ethPriceInGBP = getLatestPrice();
        require(ethPriceInGBP > 0, "Invalid price feed data");
        minDepositInWei = (MIN_DEPOSIT_GBP * 1e18) / ethPriceInGBP;
    }

    //Consent Management Functions 

    function checkConsent(uint256 tokenId, address role) public view returns (bool) {
        return batteryConsent[tokenId].consentStatus[role];
}
    function grantConsent(uint256 tokenId, address role) external onlyRole(CONSUMER_ROLE) {
        require(_exists(tokenId), "ERC721: token does not exist");
        batteryConsent[tokenId].consentStatus[role] = true;
        emit ConsentGranted(tokenId, role);
    }

    
    function revokeConsent(uint256 tokenId, address role) external onlyRole(CONSUMER_ROLE) {
        require(_exists(tokenId), "ERC721: token does not exist");
        batteryConsent[tokenId].consentStatus[role] = false;
        emit ConsentRevoked(tokenId, role);
    }

    // Role Management Functions
    function addManufacturer(address manufacturer) external onlyGovernment {
        grantRole(MANUFACTURER_ROLE, manufacturer);
        emit ManufacturerAdded(manufacturer, block.timestamp);
    }

    function removeManufacturer(address manufacturer) external onlyGovernment {
        revokeRole(MANUFACTURER_ROLE, manufacturer);
    }

    function addSupplier(address _account) external onlyRole(GOVERNMENT_ROLE) {
        grantRole(SUPPLIER_ROLE, _account);
    }

    function removeSupplier(address supplier) external onlyGovernment {
        revokeRole(SUPPLIER_ROLE, supplier);
    }

    function addRecycler(address _account) external onlyRole(GOVERNMENT_ROLE) {
        grantRole(RECYCLER_ROLE, _account);
    }

    function removeRecycler(address recycler) external onlyGovernment {
        revokeRole(RECYCLER_ROLE, recycler);
    }

    function grantConsumerRole(address _account) external onlyRole(GOVERNMENT_ROLE) {
        grantRole(CONSUMER_ROLE, _account);
    }

    function removeConsumer(address consumer) external onlyGovernment {
        revokeRole(CONSUMER_ROLE, consumer);
    }

    // Supplier Functionality
    function updateSupplyChainInfo(uint256 tokenId, string memory supplyChainData) external onlyRole(SUPPLIER_ROLE) {
        require(_exists(tokenId), "ERC721: token does not exist");
        batteryData[tokenId].supplyChainInfo = supplyChainData;
        emit SupplyChainInfoUpdated(tokenId, msg.sender, supplyChainData);
    }

    // Recycler Functionality
    function markBatteryRecycled(uint256 tokenId) external onlyRole(RECYCLER_ROLE) {
        require(_exists(tokenId), "ERC721: token does not exist");
        batteryData[tokenId].isRecycled = true;
        emit BatteryRecycled(tokenId, msg.sender);
    }

    function markBatteryReturnedToManufacturer(uint256 tokenId, address manufacturer) external onlyRole(RECYCLER_ROLE) {
    require(_exists(tokenId), "ERC721: token does not exist");
    require(hasRole(MANUFACTURER_ROLE, manufacturer), "Invalid manufacturer address");
    require(batteryData[tokenId].isRecycled, "Battery must be recycled first");
    
    batteryData[tokenId].returnedToManufacturer = true;
    emit BatteryReturnedToManufacturer(tokenId, msg.sender, manufacturer);
    
    // Transfer the token back to the manufacturer
    _transfer(ownerOf(tokenId), manufacturer, tokenId);
}

    // Deposit and Penalty Functions
    function deposit() external payable nonReentrant {
        manufacturerDeposits[msg.sender] += msg.value;
    }

    function lockDeposit() external hasMinimumDeposit nonReentrant {
        uint256 lockedDeposit = manufacturerDeposits[msg.sender];
        manufacturerDeposits[msg.sender] = 0;
        emit DepositLocked(msg.sender, lockedDeposit, block.timestamp);
    }

    function penalizeNonCompliance(address manufacturer, uint256 penaltyAmount) external onlyGovernment nonReentrant {
        uint256 manufacturerDeposit = manufacturerDeposits[manufacturer];
        require(manufacturerDeposit >= penaltyAmount, "Penalty exceeds deposit");
        manufacturerDeposits[manufacturer] -= penaltyAmount;
        emit PenaltyApplied(manufacturer, penaltyAmount, block.timestamp);
    }

    // Battery Token Functions
    function mintBatteryToken(uint256 tokenId) internal {
        _safeMint(msg.sender, tokenId);
    }

    function setBatteryData(
        uint256 tokenId, 
        string memory batteryModel, 
        string memory manufacturerLocation, 
        string memory batteryType, 
        string memory productName, 
        string memory offChainDataHash // New argument for off-chain data (IPFS hash)
    ) external onlyRole(MANUFACTURER_ROLE) {
        require(!_exists(tokenId), "ERC721: token already minted");

        batteryData[tokenId] = BatteryData({
            identification: Identification({
            batteryModel: batteryModel,
            manufacturerLocation: manufacturerLocation
        }),
        technicalSpecifications: TechnicalSpecifications({
            batteryType: batteryType
        }),
        productName: productName,
        supplyChainInfo: "", // You can set this later when needed
        isRecycled: false, // Default value for new battery
        returnedToManufacturer: false, // Default value
        offChainDataHash: offChainDataHash // Set the IPFS hash for off-chain data
    });

    _safeMint(msg.sender, tokenId);

    emit BatteryDataSet(tokenId, msg.sender, batteryModel, batteryType, productName);
}


    function viewBatteryDetails(uint256 tokenId) 
    external 
    view 
    returns (
        string memory batteryType,
        string memory batteryModel,
        string memory productName,
        string memory manufacturingSite,
        string memory supplyChainInfo,
        bool isRecycled,
        bool returnedToManufacturer,
        string memory offChainDataHash // Added for the off-chain data
    ) 
{
    // Retrieve the BatteryData struct for the given tokenId
    BatteryData memory data = batteryData[tokenId];

    // Return the relevant values
    return (
        data.technicalSpecifications.batteryType,     // batteryType
        data.identification.batteryModel,              // batteryModel
        data.productName,                              // productName
        data.identification.manufacturerLocation,      // manufacturingSite
        data.supplyChainInfo,                          // supplyChainInfo
        data.isRecycled,                               // isRecycled
        data.returnedToManufacturer,                   // returnedToManufacturer
        data.offChainDataHash                          // offChainDataHash
    );
}

    // Override Functions
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

// my name is roshan 
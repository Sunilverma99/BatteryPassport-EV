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

    // Struct to store battery data
    struct Identification {
        string batteryModel;
        string manufacturerLocation;
    }

    struct TechnicalSpecifications {
        string batteryType;
    }

    struct BatteryData {
        Identification identification;
        TechnicalSpecifications technicalSpecifications;
        string productName;
    }

    // Mapping from tokenId to BatteryData
    mapping(uint256 => BatteryData) public batteryData;

    // Events
    event DepositLocked(address indexed manufacturer, uint256 amount, uint256 timestamp);
    event ManufacturerAdded(address indexed manufacturer, uint256 timestamp);
    event ManufacturerRemoved(address indexed manufacturer, uint256 timestamp);
    event PenaltyApplied(address indexed manufacturer, uint256 amount, uint256 timestamp);

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

    modifier hasMinimumDeposit() {
        uint256 requiredDeposit = calculateMinDeposit();
        uint256 providedDeposit = manufacturerDeposits[msg.sender];
        if (providedDeposit < requiredDeposit) revert InsufficientDeposit(requiredDeposit, providedDeposit);
        _;
    }

    /**
     * @notice Fetches the latest GBP/ETH price from Chainlink.
     * @return price The latest price.
     */
    function getLatestPrice() public view returns (uint256 price) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        require(answer > 0, "Invalid price feed data");
        price = uint256(answer);
    }

    /**
     * @notice Calculates the required deposit in Ether based on a £10 minimum.
     * @return minDepositInWei The minimum deposit required in wei.
     */
    function calculateMinDeposit() public view returns (uint256 minDepositInWei) {
        uint256 ethPriceInGBP = getLatestPrice();
        require(ethPriceInGBP > 0, "Invalid price feed data");
        minDepositInWei = (MIN_DEPOSIT_GBP * 1e18) / ethPriceInGBP;
    }

    /**
     * @notice Adds a manufacturer to the system.
     * @param manufacturer The address of the manufacturer.
     */
    function addManufacturer(address manufacturer) external onlyGovernment {
        grantRole(MANUFACTURER_ROLE, manufacturer);
        emit ManufacturerAdded(manufacturer, block.timestamp);
    }

    /**
     * @notice Locks the manufacturer's deposit.
     */
    function lockDeposit() external hasMinimumDeposit nonReentrant {
        uint256 lockedDeposit = manufacturerDeposits[msg.sender]; // Renamed variable to avoid conflict
        manufacturerDeposits[msg.sender] = 0; // Lock the deposit by setting it to 0
        emit DepositLocked(msg.sender, lockedDeposit, block.timestamp);
    }

    /**
     * @notice Manufacturer can deposit Ether to the contract.
     */
    function deposit() external payable nonReentrant {
        manufacturerDeposits[msg.sender] += msg.value;
    }


    function penalizeNonCompliance(address manufacturer, uint256 penaltyAmount) external onlyGovernment nonReentrant {
        uint256 manufacturerDeposit = manufacturerDeposits[manufacturer];
        require(manufacturerDeposit >= penaltyAmount, "Penalty exceeds deposit");
        manufacturerDeposits[manufacturer] -= penaltyAmount;
        emit PenaltyApplied(manufacturer, penaltyAmount, block.timestamp);
    }

   
    function setBatteryData(uint256 tokenId, string memory batteryModel, string memory manufacturerLocation, string memory batteryType, string memory productName) external onlyRole(MANUFACTURER_ROLE) {
    batteryData[tokenId] = BatteryData({
        identification: Identification({
            batteryModel: batteryModel,
            manufacturerLocation: manufacturerLocation
        }),
        technicalSpecifications: TechnicalSpecifications({
            batteryType: batteryType
        }),
        productName: productName
    });
}

    /**
     * @notice Views battery details after consent is given.
     * @param tokenId The token ID of the battery.
     * @return batteryType The type of the battery.
     * @return batteryModel The model of the battery.
     * @return productName The name of the product.
     * @return manufacturingSite The manufacturing site of the battery.
     */
    function viewBatteryDetails(uint256 tokenId)
        external
        view
        onlyRole(CONSUMER_ROLE)
        returns (
            string memory batteryType,
            string memory batteryModel,
            string memory productName,
            string memory manufacturingSite
        )
    {
        BatteryData storage data = batteryData[tokenId];

        batteryType = data.technicalSpecifications.batteryType;
        batteryModel = data.identification.batteryModel;
        productName = data.productName;
        manufacturingSite = data.identification.manufacturerLocation;
    }

    // Functions for removing roles (optional for testing)
    /**
     * @notice Removes a manufacturer from the system.
     * @param manufacturer The address of the manufacturer.
     */
    function removeManufacturer(address manufacturer) external onlyGovernment {
        revokeRole(MANUFACTURER_ROLE, manufacturer);
    }

    /**
     * @dev See {IERC165-supportsInterface}.
     */
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

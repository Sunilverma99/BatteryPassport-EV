// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

// Import necessary OpenZeppelin contracts
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
/**
 * @title EVBatteryPassport
 * @dev A smart contract for managing EV battery passports in compliance with EU regulations.
 */
contract EVBatteryPassport is ERC721, AccessControl, ReentrancyGuard {
    using Strings for uint256;

    // Role definitions using AccessControl
    bytes32 public constant GOVERNMENT_ROLE = DEFAULT_ADMIN_ROLE;
    bytes32 public constant MANUFACTURER_ROLE = keccak256("MANUFACTURER_ROLE");
    bytes32 public constant SUPPLIER_ROLE = keccak256("SUPPLIER_ROLE");
    bytes32 public constant RECYCLER_ROLE = keccak256("RECYCLER_ROLE");
    bytes32 public constant CONSUMER_ROLE = keccak256("CONSUMER_ROLE");

    // Chainlink price feed for GBP/ETH conversion
    AggregatorV3Interface internal priceFeed;

    // Minimum deposit amount in GBP (set to £10 with 18 decimals)
    uint256 public constant MIN_DEPOSIT_GBP = 10 * 10**18;

    // Mapping to store manufacturer deposits
    mapping(address => uint256) public manufacturerDeposits;

    // Mapping to track the number of active batteries per manufacturer
    mapping(address => uint256) private manufacturerActiveBatteries;

    // Consent mapping for consumers
    mapping(address => bool) public consentGiven;

    // Mapping for battery data (tokenId => BatteryData)
    mapping(uint256 => BatteryData) private batteryData;

    // Mapping to ensure unique Battery IDs
    mapping(string => bool) private usedUniqueBatteryIDs;

    // Mapping for authorized suppliers per battery (tokenId => supplier address => bool)
    mapping(uint256 => mapping(address => bool)) private authorizedSuppliers;

    // Mapping for assigned recyclers per battery (tokenId => recycler address)
    mapping(uint256 => address) private batteryRecyclers;

    // Custom errors for gas efficiency
    error OnlyGovernment();
    error OnlyManufacturer();
    error OnlySupplier();
    error OnlyRecycler();
    error OnlyConsumer();
    error InsufficientDeposit(uint256 required, uint256 provided);
    error NoDepositToRefund();
    error PenaltyExceedsDeposit();
    error ConsentNotGiven();
    error UnauthorizedUpdate();
    error InvalidInput(string reason);
    error BatteryAlreadyCollected();
    error BatteryNotCollected();
    error BatteryAlreadyRecycled();

    // Events
    event BatteryMinted(uint256 indexed tokenId, address indexed manufacturer, uint256 timestamp);
    event BatteryUpdated(uint256 indexed tokenId, address indexed updatedBy, string dataType, uint256 timestamp);
    event BatteryVerified(uint256 indexed tokenId, address indexed verifier, uint256 timestamp, string verificationStatus);
    event ConsumerReportSubmitted(uint256 indexed tokenId, string report, address indexed submittedBy, uint256 timestamp);
    event BatteryTakenBack(uint256 indexed tokenId, string recyclingFacility, address indexed submittedBy, uint256 timestamp);
    event BatteryRecycled(uint256 indexed tokenId, address indexed recycler, uint256 timestamp);
    event RecycledBatteryDataUpdated(uint256 indexed tokenId, uint256 timestamp);
    event ConsentGiven(address indexed consumer, uint256 timestamp);
    event ConsentRevoked(address indexed consumer, uint256 timestamp);
    event SupplierAuthorized(uint256 indexed tokenId, address indexed supplier, uint256 timestamp);
    event SupplierAuthorizationRevoked(uint256 indexed tokenId, address indexed supplier, uint256 timestamp);
    event RecyclerAssigned(uint256 indexed tokenId, address indexed recycler, uint256 timestamp);
    event DepositRefunded(address indexed manufacturer, uint256 amount, uint256 timestamp);
    event DepositLocked(address indexed manufacturer, uint256 amount, uint256 timestamp);

    // Enumerations for fixed options
    enum BatteryType { LithiumIon, LeadAcid, NickelMetalHydride, Other }
    enum BatteryChemistry { NMC, LFP, LMO, NCA, Other }

    // BatteryData struct divided into sub-structs
    struct BatteryData {
        BatteryIdentification identification;
        TechnicalSpecifications technicalSpecifications;
        MaterialsComposition materialsComposition;
        PerformanceData performanceData;
        SustainabilityData sustainabilityData;
        SupplyChainInfo supplyChainInfo;
        MaintenanceInfo maintenanceInfo;
        EndOfLifeManagement endOfLifeManagement;
        TrackingData trackingData;
        address manufacturer; // Added to track the manufacturer
        string productName; // New field for Product Name
       //ChainOfCustody[] chainOfCustody; // New field for Chain of Custody
    }

    struct ChainOfCustody {
        string eventType; // e.g., "Serviced", "Sold to Consumer", "Installed in Vehicle"
        string details; // Additional details about the event
        uint256 timestamp; // When the event occurred
    }

    // Sub-structs
    struct BatteryIdentification {
        string uniqueBatteryID;
        string manufacturerName;
        string manufacturerLocation;
        string countryOfOrigin;
        string productionDate;
        string batteryModel;
        string intendedUse;
        string warrantyIdentifier;
        string certificationMarks;
        string environmentalCertifications;
        string safetyStandardsComplianceID;
        string oemIdentifier;
        string blockchainTraceabilityCode;
        string smartContractID;
    }

    struct TechnicalSpecifications {
        uint256 capacity; // Wh or mAh
        uint256 voltage; // in mV to avoid decimals
        uint256 weight; // in grams
        uint256 dimensions; // as an encoded value
        BatteryType batteryType;
        BatteryChemistry batteryChemistry;
    }

    struct MaterialsComposition {
        string listOfMaterials;
        string hazardousSubstances;
        uint256 percentageOfCRMs;
        uint256 recycledContent; // percentage
        string conflictMineralReporting;
        string supplierInfoForRawMaterials;
        string msds; // Material Safety Data Sheet
        string cathodeMaterials;
        string anodeMaterials;
        string electrolyteComposition;
        string casingMaterial;
        uint256 recyclabilityOfMaterials; // percentage
    }

    struct PerformanceData {
        uint256 cycleLife;
        uint256 stateOfHealth; // SoH percentage
        uint256 stateOfCharge; // SoC percentage
        uint256 energyEfficiency; // percentage
        uint256 depthOfDischarge; // DoD percentage
        uint256 chargingTime; // in minutes
        uint256 dischargeRate; // in C-rate
        int256 temperatureRangeMin; // in Celsius
        int256 temperatureRangeMax; // in Celsius
        uint256 selfDischargeRate; // percentage per month
    }

    struct SustainabilityData {
        uint256 environmentalFootprint; // e.g., kg CO₂e
        string regulatoryCompliance;
        string endOfLifeRecyclingInstructions;
        uint256 recyclabilityPercentage;
        string hazardousSubstanceDeclaration;
        string batteryDirectiveCompliance;
        uint256 recycledMaterialContent; // percentage
        string lifecycleAssessment;
    }

    struct SupplyChainInfo {
        string sourceOfMaterials;
        string manufacturingProcesses;
        string materialTraceability;
        string supplierSustainabilityCertifications;
        string logisticsAndTransportationData;
        string dueDiligencePolicy;
    }

    struct MaintenanceInfo {
        string recommendedMaintenance;
        string repairability;
        string softwareUpdates;
        string batteryHealthMonitoringGuidelines;
        string safetyInstructions;
        string endOfLifeManagementInstructions;
        string warrantyInformation;
        string accessToSpareParts;
        string serviceManual;
    }

    struct EndOfLifeManagement {
        bool isCollected;
        bool isRecycled;
        string recyclingInstructions;
        uint256 recyclabilityRate; // percentage
        string collectionSchemeInfo;
        string dismantlingGuidelines;
        string secondLifePotential;
        string recyclingFacility;
    }

    struct TrackingData {
        string usageHistory;
        uint256 cycleCount;
        string endOfLifeAlerts;
        uint256 carbonFootprintTracking;
    }

    /**
     * @notice Constructor to set up roles and initialize the contract.
     * @param _government The address assigned the GOVERNMENT_ROLE.
     * @param _priceFeed The address of the Chainlink price feed.
     */
    constructor(address _government, address _priceFeed)
        ERC721("EVBatteryPassport", "EVBP")
    {
        // Set up roles
        _setupRole(GOVERNMENT_ROLE, _government);
        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    // Modifiers using AccessControl

    modifier onlyGovernment() {
        if (!hasRole(GOVERNMENT_ROLE, msg.sender)) revert OnlyGovernment();
        _;
    }

    modifier onlyManufacturer() {
        if (!hasRole(MANUFACTURER_ROLE, msg.sender)) revert OnlyManufacturer();
        _;
    }

    modifier onlySupplier() {
        if (!hasRole(SUPPLIER_ROLE, msg.sender)) revert OnlySupplier();
        _;
    }

    modifier onlyRecycler() {
        if (!hasRole(RECYCLER_ROLE, msg.sender)) revert OnlyRecycler();
        _;
    }

    modifier onlyConsumer() {
        if (!hasRole(CONSUMER_ROLE, msg.sender)) revert OnlyConsumer();
        _;
    }

    modifier hasMinimumDeposit() {
        uint256 requiredDeposit = calculateMinDeposit();
        uint256 providedDeposit = manufacturerDeposits[msg.sender];
        if (providedDeposit < requiredDeposit) revert InsufficientDeposit(requiredDeposit, providedDeposit);
        _;
    }

    modifier withConsent() {
        if (!consentGiven[msg.sender]) revert ConsentNotGiven();
        _;
    }

    modifier onlyBatteryOwner(uint256 tokenId) {
        if (ownerOf(tokenId) != msg.sender) revert UnauthorizedUpdate();
        _;
    }

    modifier onlyAuthorizedSupplier(uint256 tokenId) {
        if (!authorizedSuppliers[tokenId][msg.sender]) revert UnauthorizedUpdate();
        _;
    }

    modifier onlyAssignedRecycler(uint256 tokenId) {
        if (batteryRecyclers[tokenId] != msg.sender) revert UnauthorizedUpdate();
        _;
    }

    // Functions
    /**
    * @dev See {IERC165-supportsInterface}.
    */
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
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
    }

    /**
     * @notice Removes a manufacturer from the system.
     * @param manufacturer The address of the manufacturer.
     */
    function removeManufacturer(address manufacturer) external onlyGovernment {
        revokeRole(MANUFACTURER_ROLE, manufacturer);
    }

    // Similar functions for suppliers, recyclers, and consumers...

    /**
     * @notice Adds a supplier to the system.
     * @param supplier The address of the supplier.
     */
    function addSupplier(address supplier) external onlyGovernment {
        grantRole(SUPPLIER_ROLE, supplier);
    }

    /**
     * @notice Removes a supplier from the system.
     * @param supplier The address of the supplier.
     */
    function removeSupplier(address supplier) external onlyGovernment {
        revokeRole(SUPPLIER_ROLE, supplier);
    }

    /**
     * @notice Adds a recycler to the system.
     * @param recycler The address of the recycler.
     */
    function addRecycler(address recycler) external onlyGovernment {
        grantRole(RECYCLER_ROLE, recycler);
    }

    /**
     * @notice Removes a recycler from the system.
     * @param recycler The address of the recycler.
     */
    function removeRecycler(address recycler) external onlyGovernment {
        revokeRole(RECYCLER_ROLE, recycler);
    }

    /**
     * @notice Adds a consumer to the system.
     * @param consumer The address of the consumer.
     */
    function addConsumer(address consumer) external onlyGovernment {
        grantRole(CONSUMER_ROLE, consumer);
    }

    /**
     * @notice Removes a consumer from the system.
     * @param consumer The address of the consumer.
     */
    function removeConsumer(address consumer) external onlyGovernment {
        revokeRole(CONSUMER_ROLE, consumer);
    }

    /**
     * @notice Manufacturers lock deposits to ensure compliance with recycling.
     */
    function lockDeposit() external payable onlyManufacturer {
        if (msg.value == 0) revert InvalidInput("Must deposit a valid amount");
        manufacturerDeposits[msg.sender] += msg.value;
        emit DepositLocked(msg.sender, msg.value, block.timestamp);
    }

    /**
     * @notice Allows manufacturers to refund their deposits.
     */
    function refundDeposit() external onlyManufacturer nonReentrant {
        require(manufacturerActiveBatteries[msg.sender] == 0, "Active batteries exist");
        uint256 deposit = manufacturerDeposits[msg.sender];
        if (deposit == 0) revert NoDepositToRefund();
        
        manufacturerDeposits[msg.sender] = 0;
        
        (bool success, ) = msg.sender.call{value: deposit}("");
        require(success, "Refund transfer failed");
        
        emit DepositRefunded(msg.sender, deposit, block.timestamp);
    }

    /**
     * @notice Penalizes a manufacturer for non-compliance.
     * @param manufacturer The address of the manufacturer.
     * @param penaltyAmount The amount to penalize.
     */
    function penalizeNonCompliance(address manufacturer, uint256 penaltyAmount)
        external
        onlyGovernment
        nonReentrant
    {
        uint256 deposit = manufacturerDeposits[manufacturer];
        if (deposit < penaltyAmount) revert PenaltyExceedsDeposit();
        manufacturerDeposits[manufacturer] -= penaltyAmount;
    }

    /**
     * @notice Mints a new battery passport NFT and records its data.
     * @param to The address receiving the NFT.
     * @param tokenId The unique token ID.
     * @param data The battery data.
     */
    function mintBatteryPassport(
        address to,
        uint256 tokenId,
        BatteryData calldata data
    ) external onlyManufacturer hasMinimumDeposit {
        require(!_exists(tokenId), "Token ID already exists");
        // Ensure immutable fields are set correctly
        require(bytes(data.identification.uniqueBatteryID).length > 0, "UniqueBatteryID is required");
        require(!usedUniqueBatteryIDs[data.identification.uniqueBatteryID], "uniqueBatteryID already used");
        usedUniqueBatteryIDs[data.identification.uniqueBatteryID] = true;

        // Update manufacturer's active battery count
        manufacturerActiveBatteries[msg.sender] += 1;

        // Set the manufacturer address in the battery data
        BatteryData memory newData = data;
        newData.manufacturer = msg.sender;

        _safeMint(to, tokenId);
        batteryData[tokenId] = newData;
        emit BatteryMinted(tokenId, msg.sender, block.timestamp);
    }

    // Functions to authorize suppliers and recyclers

    /**
     * @notice Authorizes a supplier to update a specific battery.
     * @param tokenId The token ID of the battery.
     * @param supplier The address of the supplier.
     */
    function authorizeSupplier(uint256 tokenId, address supplier)
        external
        onlyManufacturer
        onlyBatteryOwner(tokenId)
    {
        require(hasRole(SUPPLIER_ROLE, supplier), "Address is not a supplier");
        authorizedSuppliers[tokenId][supplier] = true;
        emit SupplierAuthorized(tokenId, supplier, block.timestamp);
    }

    /**
     * @notice Revokes a supplier's authorization for a specific battery.
     * @param tokenId The token ID of the battery.
     * @param supplier The address of the supplier.
     */
    function revokeSupplierAuthorization(uint256 tokenId, address supplier)
        external
        onlyManufacturer
        onlyBatteryOwner(tokenId)
    {
        authorizedSuppliers[tokenId][supplier] = false;
        emit SupplierAuthorizationRevoked(tokenId, supplier, block.timestamp);
    }

    /**
     * @notice Assigns a recycler to a specific battery.
     * @param tokenId The token ID of the battery.
     * @param recycler The address of the recycler.
     */
    function assignRecyclerToBattery(uint256 tokenId, address recycler)
        external
        onlyGovernment
    {
        require(hasRole(RECYCLER_ROLE, recycler), "Address is not a recycler");
        batteryRecyclers[tokenId] = recycler;
        emit RecyclerAssigned(tokenId, recycler, block.timestamp);
    }

    // Update functions with proper access control and data validation

    /**
     * @notice Updates the technical specifications of a battery.
     * @param tokenId The token ID of the battery.
     * @param specs The updated technical specifications.
     */
    function updateTechnicalSpecifications(
        uint256 tokenId,
        TechnicalSpecifications calldata specs
    ) external onlyManufacturer hasMinimumDeposit onlyBatteryOwner(tokenId) {
        require(specs.capacity > 0, "Capacity must be positive");
        require(specs.voltage > 0, "Voltage must be positive");
        require(specs.weight > 0, "Weight must be positive");
        // Additional validations as needed

        batteryData[tokenId].technicalSpecifications = specs;
        emit BatteryUpdated(tokenId, msg.sender, "TechnicalSpecifications", block.timestamp);
    }

    /**
     * @notice Updates the materials composition of a battery.
     * @param tokenId The token ID of the battery.
     * @param composition The updated materials composition.
     */
    function updateMaterialsComposition(
        uint256 tokenId,
        MaterialsComposition calldata composition
    ) external onlyManufacturer hasMinimumDeposit onlyBatteryOwner(tokenId) {
        require(composition.percentageOfCRMs <= 100, "Percentage of CRMs must be <= 100%");
        require(composition.recycledContent <= 100, "Recycled content must be <= 100%");
        require(composition.recyclabilityOfMaterials <= 100, "Recyclability must be <= 100%");
        // Additional validations as needed

        batteryData[tokenId].materialsComposition = composition;
        emit BatteryUpdated(tokenId, msg.sender, "MaterialsComposition", block.timestamp);
    }

    /**
     * @notice Updates the sustainability data of a battery.
     * @param tokenId The token ID of the battery.
     * @param data The updated sustainability data.
     */
    function updateSustainabilityData(
        uint256 tokenId,
        SustainabilityData calldata data
    ) external onlyManufacturer hasMinimumDeposit onlyBatteryOwner(tokenId) {
        require(data.recyclabilityPercentage <= 100, "Recyclability percentage must be <= 100%");
        require(data.recycledMaterialContent <= 100, "Recycled material content must be <= 100%");
        // Additional validations as needed

        batteryData[tokenId].sustainabilityData = data;
        emit BatteryUpdated(tokenId, msg.sender, "SustainabilityData", block.timestamp);
    }

    /**
     * @notice Updates the supply chain information of a battery.
     * @param tokenId The token ID of the battery.
     * @param info The updated supply chain information.
     */
    function updateSupplyChainInfo(
        uint256 tokenId,
        SupplyChainInfo calldata info
    ) external onlySupplier onlyAuthorizedSupplier(tokenId) {
        // Add validations if necessary

        batteryData[tokenId].supplyChainInfo = info;
        emit BatteryUpdated(tokenId, msg.sender, "SupplyChainInfo", block.timestamp);
    }

    /**
     * @notice Updates the end-of-life management data of a battery.
     * @param tokenId The token ID of the battery.
     * @param eolData The updated end-of-life management data.
     */
    function updateEndOfLifeManagement(
        uint256 tokenId,
        EndOfLifeManagement calldata eolData
    ) external onlyRecycler onlyAssignedRecycler(tokenId) {
        require(eolData.recyclabilityRate <= 100, "Recyclability rate must be <= 100%");
        // Additional validations as needed

        batteryData[tokenId].endOfLifeManagement = eolData;
        emit BatteryUpdated(tokenId, msg.sender, "EndOfLifeManagement", block.timestamp);
    }

    /**
     * @notice Updates the performance data of a battery.
     * @param tokenId The token ID of the battery.
     * @param data The updated performance data.
     */
    function updatePerformanceData(
        uint256 tokenId,
        PerformanceData calldata data
    ) external onlyManufacturer hasMinimumDeposit onlyBatteryOwner(tokenId) {
        require(data.stateOfHealth <= 100, "State of Health must be <= 100%");
        require(data.stateOfCharge <= 100, "State of Charge must be <= 100%");
        require(data.energyEfficiency <= 100, "Energy Efficiency must be <= 100%");
        require(data.depthOfDischarge <= 100, "Depth of Discharge must be <= 100%");
        require(data.selfDischargeRate <= 100, "Self-Discharge Rate must be <= 100%");
        require(data.cycleLife > 0, "Cycle Life must be positive");
        // Additional validations as needed

        batteryData[tokenId].performanceData = data;
        emit BatteryUpdated(tokenId, msg.sender, "PerformanceData", block.timestamp);
    }

    /**
     * @notice Updates the maintenance information of a battery.
     * @param tokenId The token ID of the battery.
     * @param info The updated maintenance information.
     */
    function updateMaintenanceInfo(
        uint256 tokenId,
        MaintenanceInfo calldata info
    ) external onlyManufacturer hasMinimumDeposit onlyBatteryOwner(tokenId) {
        // Add validations if necessary

        batteryData[tokenId].maintenanceInfo = info;
        emit BatteryUpdated(tokenId, msg.sender, "MaintenanceInfo", block.timestamp);
    }

    /**
     * @notice Updates the tracking data of a battery.
     * @param tokenId The token ID of the battery.
     * @param data The updated tracking data.
     */
    function updateTrackingData(
        uint256 tokenId,
        TrackingData calldata data
    ) external onlySupplier onlyAuthorizedSupplier(tokenId) {
        require(data.cycleCount >= 0, "Cycle count cannot be negative");
        // Additional validations as needed

        batteryData[tokenId].trackingData = data;
        emit BatteryUpdated(tokenId, msg.sender, "TrackingData", block.timestamp);
    }

    /**
     * @notice Allows consumers to give consent to view battery details.
     */
    function giveConsent() external onlyConsumer {
        consentGiven[msg.sender] = true;
        emit ConsentGiven(msg.sender, block.timestamp);
    }

    /**
     * @notice Allows consumers to revoke consent.
     */
    function revokeConsent() external onlyConsumer {
        consentGiven[msg.sender] = false;
        emit ConsentRevoked(msg.sender, block.timestamp);
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
        onlyConsumer
        withConsent
        onlyBatteryOwner(tokenId)
        returns (
            string memory batteryType,
            //string memory durability,
            string memory batteryModel,
            //string memory performance,
            string memory productName,
            string memory manufacturingSite
            //string memory recycledContent,
            //string memory endOfLifeCollectionInfo,
            //string memory batteryHealth,
            //string memory ghgEmissions,
            //string memory declarationOfConformity,
            //string memory hazardousSubstances,
            //string memory certifications,
            //string memory dueDiligencePolicy,
            //ChainOfCustody[] memory chainOfCustody
        )
    {
        BatteryData storage data = batteryData[tokenId];

        batteryType = getBatteryType(data.technicalSpecifications.batteryType);
        //durability = getDurability(data.performanceData);
        batteryModel = data.identification.batteryModel;
        //performance = getPerformance(data.performanceData);
        productName = data.productName;
        manufacturingSite = data.identification.manufacturerLocation;
        //recycledContent = getRecycledContent(data.materialsComposition.recycledContent);
        //endOfLifeCollectionInfo = data.endOfLifeManagement.collectionSchemeInfo;
        //batteryHealth = getBatteryHealth(data.performanceData.stateOfHealth);
        //ghgEmissions = getGHGEmissions(data.sustainabilityData.environmentalFootprint);
        //declarationOfConformity = data.identification.certificationMarks;
        //hazardousSubstances = data.materialsComposition.hazardousSubstances;
        //certifications = data.identification.environmentalCertifications;
        //dueDiligencePolicy = data.supplyChainInfo.dueDiligencePolicy;
        //chainOfCustody = data.chainOfCustody;
    }


    /**
     * @notice Converts the BatteryType enum to a string.
     */
    function getBatteryType(BatteryType batteryType) internal pure returns (string memory) {
        if (batteryType == BatteryType.LithiumIon) return "Lithium Ion";
        if (batteryType == BatteryType.LeadAcid) return "Lead Acid";
        if (batteryType == BatteryType.NickelMetalHydride) return "Nickel Metal Hydride";
        return "Other";
    }

    /**
     * @notice Generates a durability string based on performance data.
     */
    function getDurability(PerformanceData memory performanceData) internal pure returns (string memory) {
        // Add logic to calculate durability based on performance data
        return "Durability based on performance data";
    }

    /**
     * @notice Generates a performance string based on performance data.
     */
    function getPerformance(PerformanceData memory performanceData) internal pure returns (string memory) {
        // Add logic to summarize performance data
        return "Performance summary";
    }

    /**
     * @notice Converts the recycled content to a string.
     */
    function getRecycledContent(uint256 recycledContent) internal pure returns (string memory) {
        return string(abi.encodePacked(recycledContent.toString(), "%"));
    }

    /**
     * @notice Converts the state of health to a string.
     */
    function getBatteryHealth(uint256 stateOfHealth) internal pure returns (string memory) {
        return string(abi.encodePacked(stateOfHealth.toString(), "% SoH"));
    }

    /**
     * @notice Converts the GHG emissions to a string.
     */
    function getGHGEmissions(uint256 environmentalFootprint) internal pure returns (string memory) {
        return string(abi.encodePacked(environmentalFootprint.toString(), " kg CO2e"));
    }

    /**
     * @notice Verifies the battery data.
     * @param tokenId The token ID of the battery.
     * @param verificationStatus The status of the verification.
     */
    function verifyBattery(uint256 tokenId, string calldata verificationStatus)
        external
        onlyGovernment
    {
        // Implement verification logic if needed
        emit BatteryVerified(tokenId, msg.sender, block.timestamp, verificationStatus);
    }

    /**
     * @notice Submits a consumer report on battery performance or issues.
     * @param tokenId The token ID of the battery.
     * @param report The consumer report.
     */
    function submitConsumerReport(uint256 tokenId, string calldata report)
        external
        onlyConsumer
        onlyBatteryOwner(tokenId)
    {
        emit ConsumerReportSubmitted(tokenId, report, msg.sender, block.timestamp);
    }

    // Functions for battery take-back and recycling

    /**
     * @notice Initiates the take-back process for an end-of-life battery.
     * @param tokenId The token ID of the battery.
     * @param recyclingFacility The designated recycling facility.
     */
    function takeBackBattery(uint256 tokenId, string calldata recyclingFacility)
        external
        onlyConsumer
        onlyBatteryOwner(tokenId)
    {
        EndOfLifeManagement storage eolData = batteryData[tokenId].endOfLifeManagement;
        if (eolData.isCollected) revert BatteryAlreadyCollected();
        eolData.isCollected = true;
        eolData.recyclingFacility = recyclingFacility;
        emit BatteryTakenBack(tokenId, recyclingFacility, msg.sender, block.timestamp);
    }

    /**
     * @notice Confirms the recycling of a battery.
     * @param tokenId The token ID of the battery.
     */
    function confirmRecycling(uint256 tokenId)
        external
        onlyRecycler
        onlyAssignedRecycler(tokenId)
    {
        EndOfLifeManagement storage eolData = batteryData[tokenId].endOfLifeManagement;
        if (!eolData.isCollected) revert BatteryNotCollected();
        if (eolData.isRecycled) revert BatteryAlreadyRecycled();
        eolData.isRecycled = true;

        // Decrease manufacturer's active battery count
        address manufacturer = batteryData[tokenId].manufacturer;
        if (manufacturerActiveBatteries[manufacturer] > 0) {
            manufacturerActiveBatteries[manufacturer] -= 1;
        }

        emit BatteryRecycled(tokenId, msg.sender, block.timestamp);
    }

    /**
     * @notice Updates recycled battery data.
     * @param tokenId The token ID of the battery.
     * @param eolData The updated end-of-life management data.
     */
    function updateRecycledBatteryData(uint256 tokenId, EndOfLifeManagement calldata eolData)
        external
        onlyRecycler
        onlyAssignedRecycler(tokenId)
    {
        require(eolData.recyclabilityRate <= 100, "Recyclability rate must be <= 100%");
        // Additional validations as needed

        batteryData[tokenId].endOfLifeManagement = eolData;
        emit RecycledBatteryDataUpdated(tokenId, block.timestamp);
    }

    // Additional functions for government updates

    /**
     * @notice Updates the regulatory compliance of a battery.
     * @param tokenId The token ID of the battery.
     * @param compliance The updated regulatory compliance status.
     */
    function updateRegulatoryCompliance(
        uint256 tokenId,
        string calldata compliance
    ) external onlyGovernment {
        batteryData[tokenId].sustainabilityData.regulatoryCompliance = compliance;
        emit BatteryUpdated(tokenId, msg.sender, "RegulatoryCompliance", block.timestamp);
    }

    /**
     * @notice Updates the product name of a battery.
     * @param tokenId The token ID of the battery.
     * @param productName The new product name.
     */
    function updateProductName(
        uint256 tokenId,
        string calldata productName
    ) external onlyManufacturer onlyBatteryOwner(tokenId) {
        require(bytes(productName).length > 0, "Product name cannot be empty");
        batteryData[tokenId].productName = productName;
        emit BatteryUpdated(tokenId, msg.sender, "ProductName", block.timestamp);
    }

    /**
     * @notice Updates the supply chain due diligence policy of a battery.
     * @param tokenId The token ID of the battery.
     * @param policy The new due diligence policy.
     */
    function updateSupplyChainDueDiligencePolicy(
        uint256 tokenId,
        string calldata policy
    ) external onlySupplier onlyAuthorizedSupplier(tokenId) {
        require(bytes(policy).length > 0, "Policy cannot be empty");
        batteryData[tokenId].supplyChainInfo.dueDiligencePolicy = policy;
        emit BatteryUpdated(tokenId, msg.sender, "SupplyChainDueDiligencePolicy", block.timestamp);
    }
    /** 
    /**
     * @notice Logs a chain of custody event for a battery.
     * @param tokenId The token ID of the battery.
     * @param eventType The type of custody event.
     * @param details Additional details about the event.
     */
    //function logChainOfCustody(
       // uint256 tokenId,
      //  string calldata eventType,
      //  string calldata details
   // ) external onlyBatteryOwner(tokenId) {
        //require(bytes(eventType).length > 0, "Event type cannot be empty");
        //require(bytes(details).length > 0, "Details cannot be empty");

       // ChainOfCustody memory newEvent = ChainOfCustody({
           // eventType: eventType,
            //details: details,
            //timestamp: block.timestamp
       // });

        //batteryData[tokenId].chainOfCustody.push(newEvent);
        //emit BatteryUpdated(tokenId, msg.sender, "ChainOfCustody", block.timestamp);
    //}


    // Overridden functions from ERC721 if necessary

    /**
    * @dev Overrides the _beforeTokenTransfer function to include custom logic.
    *      Prevents transferring the NFT if certain conditions are not met.
    */
    function _beforeTokenTransfer(
        address from,
        address to,
        uint256 firstTokenId,
        uint256 batchSize
    ) internal override {
        super._beforeTokenTransfer(from, to, firstTokenId, batchSize);
        // Uncomment the following line to prevent transfer if battery is not recycled
        // require(
        //     batteryData[firstTokenId].endOfLifeManagement.isRecycled,
        //     "Battery must be recycled before transfer"
        // );
}

}


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

// Import the Chainlink MockV3Aggregator contract
import "@chainlink/contracts/src/v0.8/tests/MockV3Aggregator.sol";

// Create a mock price feed contract inheriting from MockV3Aggregator
contract MockPriceFeed is MockV3Aggregator {
    // Constructor initializes the MockV3Aggregator with the number of decimals and initial price
    constructor() MockV3Aggregator(18, 20000000000000000000) {} // 20,000 GBP with 18 decimals
}

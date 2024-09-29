// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@chainlink/contracts/src/v0.8/tests/MockV3Aggregator.sol";

contract MockPriceFeed is MockV3Aggregator {
    constructor() MockV3Aggregator(8, 2000 * 10**8) {} // 2000 USD with 8 decimals
}
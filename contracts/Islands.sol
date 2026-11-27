// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {IslandsCore} from "./IslandsCore.sol";
import {IslandsFees} from "./IslandsFees.sol";
/// @notice Production configuration remains fixed; minting starts disabled.
contract Islands is IslandsCore {
    constructor() IslandsCore(IslandsFees.KEY,IslandsFees.CREATOR,IslandsFees.MINT_PROCEEDS_RECIPIENT,"ISLANDS","ISLANDS") {}
}

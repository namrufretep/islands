// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;
import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {IslandsCore} from "./IslandsCore.sol";

/// @notice Freely issued, worthless test tokens. Deployable only on Base Sepolia.
contract IslandsTestKey is ERC20 {
    constructor() ERC20("ISLANDS TEST KEY - NO VALUE","tKEY") { require(block.chainid == 84532,"Base Sepolia only"); }
    function faucet(address recipient) external {
        require(block.chainid == 84532 && recipient != address(0),"Invalid test faucet");
        _mint(recipient,1000000 ether);
    }
}
/// @notice Receives only the test payments for this test environment.
contract IslandsTestTreasury {}
contract IslandsTestCollection is IslandsCore {
    uint256 public constant TESTNET_CHAIN_ID = 84532;
    constructor(address testKey,address creator,address treasury)
        IslandsCore(testKey,creator,treasury,"ISLANDS TEST ONLY","ISLANDS-TEST") {
        require(block.chainid == 84532,"Base Sepolia only");
        collectionMetadataURI = "https://islands-kappa.vercel.app/testnet/collection.json";
    }
}
/// @notice Creates a wholly separate token, collection and treasury in one wallet confirmation.
contract IslandsTestSuite {
    string public constant VERSION = "ISLANDS_TESTNET_V1";
    IslandsTestKey public immutable key;
    IslandsTestCollection public immutable collection;
    IslandsTestTreasury public immutable treasury;
    constructor() {
        require(block.chainid == 84532,"Base Sepolia only");
        key = new IslandsTestKey();
        treasury = new IslandsTestTreasury();
        collection = new IslandsTestCollection(address(key),address(this),address(treasury));
        collection.setMintOffer(1,"https://islands-kappa.vercel.app/testnet/edition.json",750000 ether);
        collection.setKeyMintEnabled(true);
        collection.transferOwnership(msg.sender);
        key.faucet(msg.sender);
    }
}

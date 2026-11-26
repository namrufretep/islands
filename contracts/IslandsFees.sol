// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @notice Draft fee policy in whole KEY units. Settlement must normalize
/// using verified token decimals. This library does not transfer funds.
library IslandsFees {
    address internal constant KEY = address(bytes20(hex"b0ca1e094a1779018b194ac6151ece8d6f05db07"));
    address internal constant CREATOR = address(bytes20(hex"fc5708cb64604dcf6f62de5d63a051ed577e10c1"));
    // Primary mint: the creator receives the entire amount actually paid.
    // A payment implementation must use this recipient; this policy alone
    // does not collect KEY or enable public minting.
    address internal constant MINT_PROCEEDS_RECIPIENT = CREATOR;
    uint256 internal constant MINT_KEY = 500000;
    uint256 internal constant SWAP_KEY_PER_PARTICIPANT = 25000;
    uint256 internal constant ROYALTY_BPS = 1000;
    function discountBps(uint256 verifiedStakedKeys) internal pure returns (uint256) {
        if (verifiedStakedKeys >= 50) return 2500;
        if (verifiedStakedKeys >= 30) return 2000;
        if (verifiedStakedKeys >= 15) return 1500;
        if (verifiedStakedKeys >= 5) return 1000;
        if (verifiedStakedKeys >= 1) return 500;
        return 0;
    }
    function mintWholeKey(uint256 verifiedStakedKeys) internal pure returns (uint256) {
        return MINT_KEY * (10000 - discountBps(verifiedStakedKeys)) / 10000;
    }
    function royalty(uint256 saleAmount) internal pure returns (uint256) {
        return saleAmount / 10;
    }
}

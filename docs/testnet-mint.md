# ISLANDS Base Sepolia test mint

This is a separate wallet-operated test environment, not an activation of the real collection.
Open /testnet/ or the test link on the main Mint page.

## What the user does

1. Connect a wallet supporting Base Sepolia (chain ID 84532).
2. Obtain free Base Sepolia test ETH through a faucet listed at https://docs.base.org/get-started/get-funds#testnet-base-sepolia .
3. Click Create test environment and confirm one deployment. It creates an independent test ERC-20, ERC-721 and test treasury, releases only Test Edition 1, and gives the deployer 1,000,000 tKEY.
4. Approve exactly 750,000 tKEY, then confirm Mint test NFT.
5. The UI waits for successful receipts and checks the expected ERC-20 Transfer and MintedWithKey events, actual ownerOf(1), and the test-only tokenURI.

No private key, real KEY, production collection deployment or real island mint is required.
A wallet that cannot switch to Base Sepolia or deploy contracts must use the browser-wallet alternative.
The page does not silently switch to Base mainnet or send a mainnet transaction.

## Shared implementation and test isolation

IslandsCore contains the same paid-mint implementation used by both wrappers.
Islands keeps its zero-argument constructor and original fixed creator, KEY and proceeds addresses.
IslandsTestSuite, IslandsTestKey and IslandsTestCollection deploy only on chain 84532.
The suite deployer owns the test collection after setup; test proceeds go to the separate test treasury.
Test Edition 1 uses /testnet/edition.json and an explicit TEST ONLY image; it never uses /nft/<real-artwork-id>.json.
The production gallery and leaderboards do not read test data.

## Verification and build

.github/workflows/testnet-suite.yml runs the complete Foundry suite, builds with Solidity 0.8.24 and optimizer runs 200, checks EVM bytecode size limits and exports the browser artifacts.
The artifacts carry the exact source commit and a bundle checksum. Publication is separate from deploying contracts.
A saved browser deployment is restored only after matching a successful Base Sepolia creation receipt and the exact published creation bytecode. Addresses from localStorage are never blindly trusted.

## Current boundary

The page and compiled artifacts can be published without a blockchain wallet.
Actual Base Sepolia deployment and mint require the user's testnet wallet confirmations and test ETH.
Until a successful deployment receipt exists, the UI states Not deployed. No test transaction is claimed as performed merely because code compilation or local tests pass.

# OpenSea readiness — 2026-11-26

Status: metadata prepared; local contract checks pass; live mint and OpenSea settings are **not verified**. No public-network transactions were performed.

## Completed

- All 150 gallery editions have standard JSON at `/nft/<artwork-id>.json`, including absolute original image URL, name, description, attributes and an external island link. Image hashes are calculated from the actual PNG bytes.
- `/nft/collection.json` describes the collection and declares preferred creator earnings of 1,000 basis points (10%) to `0xfc5708cb64604dcf6f62de5d63a051ed577e10c1`. These legacy JSON royalty fields do not prove an OpenSea Studio setting.
- The draft contract advertises ERC-721, metadata and ERC-2981, returns 10% from `royaltyInfo`, and exposes collection metadata through `contractURI`. Only the owner may update it; updates emit `ContractURIUpdated`.
- The creator confirmed `0xfc5708cb64604dcf6f62de5d63a051ed577e10c1` as initial collection owner and creator-fee recipient. The constructor now assigns ownership directly to this address, independently of the deployment sender. A local deployment from a different wallet verified the intended owner and rejected administration by the deployer. Individual NFT transfers leave collection ownership and the royalty recipient unchanged.
- A local Ganache deployment with Solidity 0.8.24 exercised issuance of two Samosir orientations to a buyer, ownership, tokenURI, mint Transfer events, royalty rounding, metadata update access and duplicate/nonexistent token rejection. Local token IDs 9001/9002 are test values, not release allocations.
- 13 application tests and production build passed for the preceding metadata release. All eight current local EVM check groups pass. Local checks are not an audit of a production paid mint.

## Remaining before a release

1. Configure and verify an actual collection contract address and chain. There is no deployed collection address configured in this project; paid mint and inventory/payment verification are not implemented.
   The approved primary KEY payout is 100% of the amount actually paid, after any verified discount, directly to `0xfc5708cb64604dcf6f62de5d63a051ed577e10c1`. `MINT_PROCEEDS_RECIPIENT` exposes this policy; it is not an implemented KEY transfer. Implement and test atomic payment plus NFT delivery before enabling paid minting. The secondary 10% royalty does not reduce the primary mint payout.
2. Finalize the actual release inventory and on-chain token ID to artwork URI mapping. The metadata manifest is explicitly unreleased and does not define allocation.
3. Mint an authorized token on the target network and inspect its actual OpenSea asset page: correct contract/collection, owner, image, North/South orientation, name, traits and external link. The existence of public metadata URLs alone is insufficient proof of indexing.
4. In OpenSea Studio, the collection owner must confirm 10% Creator Earnings and the recipient address. This account setting has not been inspected or signed here.
5. If payment must be enforced on OpenSea, use a reviewed compatible creator-token implementation and configure its transfer validator and OpenSea enforcement. The current plain ERC-721/ERC-2981 draft has no such validator; its royalty declaration alone does not enforce payment. The `creator_fee_enforcement_compatible` local check only detects interface names and is not a security proof for any future implementation.

## Samosir artwork revision

Samosir North-Up now uses sage `#718e83` for its two existing mapped inland lakes. The original projection and lake polygon geometry were retained. 1,412 pixels changed inside the lake mask; no pixel outside the mask changed. South-Up is unchanged. The gallery points to the versioned corrected original, and the downloadable batch and overview have been updated.

## Official reference documentation

- [OpenSea metadata standards](https://docs.opensea.io/docs/metadata-standards)
- [Contract-level metadata](https://docs.opensea.io/docs/contract-level-metadata)
- [Setting creator earnings in OpenSea Studio](https://support.opensea.io/en/articles/8867026-how-do-i-set-creator-earnings-on-opensea)
- [Creator fee enforcement](https://docs.opensea.io/docs/creator-fee-enforcement)

# ISLANDS launch preparation — 27 November 2026

The agreed initial launch target remains **500 islands / 1,000 independent North-Up and South-Up editions**. Currently **100 islands / 200 artworks** are prepared. These are candidate artworks, not released mint inventory. The next 400 islands remain to be produced and reviewed.

The user completed the separate Base Sepolia test flow through Farcaster. The displayed confirmation reports test KEY payment, NFT ownership and metadata verification. This did not mint an original island and does not constitute a Base-mainnet mint or OpenSea check.

## Prepared Base candidate

`contracts/IslandsLaunch.sol` targets Base chain 8453 and uses the existing KEY address and creator configuration. It starts with paid minting disabled, no registered editions and no discount verifier. Nobody receives an original NFT merely by deploying it.

- Canonical token ID: North-Up = 2 × island ID − 1; South-Up = 2 × island ID. For island 000001 the token IDs are 1 and 2. This is a new launch allocation, not an assignment on an existing contract.
- An owner registers a slot once, with its canonical metadata URL and artwork SHA-256. Neither registration nor setting an offer creates an NFT. A slot cannot be rebound to another URI, including through owner issuance. HTTP hosting can still change bytes: published hashes detect a change but do not make hosting immutable.
- Direct mint price: **750,000 KEY**. The primary payment goes entirely to the confirmed creator wallet. Gas is separate. The old 500,000 KEY fee-library base remains a legacy/reference value for earlier tests and swap fees; it is not the launch candidate's direct price.
- Discounts: 1 / 5 / 15 / 30 / 50 staked creator keys correspond to 5 / 10 / 15 / 20 / 25 percent. Discounted direct prices: 712,500 / 675,000 / 637,500 / 600,000 / 562,500 KEY.
- Discount calls require EIP-712 authorization from an owner-appointed verifier. Quotes bind payer, NFT recipient, edition, price, metadata URI hash, stake count and block, nonce, verifier revision and expiry. Lifetime is at most 600 seconds and stake-block lag at most 300 blocks. Payer cancellation or verifier rotation invalidates outstanding quotes. This is bounded-age eligibility, not a guarantee that the stake has not changed since the referenced block.
- The verifier may be an EOA or ERC-1271 signer. It is a trust authority: contract signature verification does not itself prove BaseFriend data. The server must independently check the designated creator market's staked count, paginate holdings, exclude liquid keys, obtain the block reference and fail closed on stale/missing data. No signer secret or working signing service is configured by this change. Do not use the creator's private key in the app or a client request to decide stake counts.
- Discovery (proposed 250,000 KEY) and regional (proposed 500,000 KEY) allocation are not implemented by this direct-mint candidate. Do not simulate blind mint by allowing a client to choose the discounted edition.
- ERC-2981 declares a 10% secondary royalty. OpenSea enforcement remains unconfigured. This change does not silently replace the implementation with a transfer validator or claim enforced marketplace payments.

## Concrete review artifacts

`/launch/` provides a read-only price/edition review. Its in-app entry is visible in the signed administrator view. As with the existing artwork assets, the URL itself is public and is not private storage. `/launch/release-plan.json` is regenerated from the current metadata and original image bytes at build time. It contains all 200 allocations and hashes, with `not_released` on every entry. `/launch/artifacts.json` contains actual optimized compiled ABI/bytecode plus source-file hashes. `/launch/mainnet-check.json` records a dated, read-only Base RPC check; it is not proof of deployment or an audit.

## Checks and remaining work

Run `npm test`, `npm run build`, and optimized `forge test`. Optional `ISLANDS_BASE_FORK_URL=https://mainnet.base.org forge test --match-contract IslandsLaunchForkTest` exercises the real deployed KEY transfer implementation on a local fork without a real transaction. `scripts/check-mainnet-release.mjs` checks Base chain ID, KEY code, symbol/decimals, deployment gas estimate and `eth_call` creation simulation; it cannot sign or broadcast.

Before opening the public mint: connect and validate the staking verification service, finish shared blind/regional inventory allocation, reach the 500-island preparation target, complete wallet checkout and ownership indexing for the actual deployed address, then check a separately authorized mainnet payment and OpenSea item/creator earnings settings. No production contract has been deployed, no original island released, and no real KEY or ETH has been spent in this preparation.

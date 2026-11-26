# ISLANDS product plan

- Unique geographic island NFTs on Base, with GIS-locked coastlines.
- BaseFriend creator key discovery, wallet holdings, buy and stake flows.
- Proposed primary mint discounts: 0–25% based on staked ISLANDS creator keys.
- Planned KEY and CHEERS payments, subject to verified token contracts and pricing.
- NFT swaps and secondary sales; OpenSea compatibility.
- Keep BaseFriend app API key server-side. Use quote, prepare, wallet signature and confirm for eligible actions.
- No live contracts or payments yet.


## Approved secondary-market royalty
OpenSea creator earnings: 10% (1000 basis points), ERC-2981. Recipient: creator-confirmed Farcaster wallet on Base: 0xfc5708cb64604dcf6f62de5d63a051ed577e10c1. OpenSea enforcement compatibility must be verified before contract deployment. This is a product requirement, not an active on-chain royalty.

## Approved collection ownership (2026-11-26)
The creator confirmed `0xfc5708cb64604dcf6f62de5d63a051ed577e10c1` as both initial collection owner and 10% creator-fee recipient, including the intended OpenSea creator identity. The draft constructor sets `Ownable(CREATOR)` without accepting an arbitrary initial owner. A deployment wallet receives no collection administration privileges unless it is that creator wallet. Ownership remains transferable by the current owner under Ownable; individual NFT transfers do not change it. Verify the actual deployed `owner()`, OpenSea creator attribution and royalty settings with a real mint before a public release. No deployment or OpenSea indexing has occurred as part of this confirmation.


## In-app secondary transactions
Required creator fee on in-app resales: 10% of actual sale consideration, paid to 0xfc5708cb64604dcf6f62de5d63a051ed577e10c1. Direct NFT-for-NFT swaps also require a creator fee; approved basis is 10% of the undiscounted 500000 KEY mint price (50000 KEY per swap total), split equally: each participant pays 25000 KEY. Both payments and NFT transfers must settle atomically. CHEERS equivalent requires verified pricing. Settlement must be atomic, enforce fees in contract, and avoid double charging royalties. No deployed contract or active settlement yet.


## Canonical geographic scale policy
All islands receive equal visual prominence regardless of real area. Canonical canvas 2048 x 2048 px at 300 dpi; uniformly fit the longest projected bounding-box dimension to 1536 px (75% of canvas), center without stretching. Use a documented locally appropriate metric projection, record CRS, distortion limitations, projected extent, meters per pixel, true geographic area and orientation. Derive the scale bar from the actual artwork transform, and scale it responsively with the image. Display it outside the art in the app; no text or labels in the NFT artwork. Store nominal print scale at 300 dpi separately from digital meters per pixel. First candidate: Bouvetoya, Glacial Turquoise. Verified licensed coastline required before canonical art publication.


## Canonical Dual Edition System (approved 2026-11-22)
This supersedes earlier one-NFT-per-island and optional orientation rules. Each geographical island has one stable geographic ID and exactly two independent ERC-721 1/1 editions: North-Up (N) and South-Up (S), with separate unique token IDs. Display IDs for Bouvetoya: #000001-N and #000001-S. Both use the same verified coastline, geographic metadata, calibrated scale and color mood. South-Up rotates the geographic orientation 180 degrees and receives independently designed light and shadow surfaces, not just a rotated copy. Each edition costs 500,000 KEY before verified staking discounts; existing fees apply independently. Viewer rotation does not change canonical art, metadata or ownership. Reset restores each edition's own canonical orientation. Contract must enforce uniqueness of geographic ID plus edition, and both editions remain independently transferable. Existing draft contract still requires revision before deployment.


## World Island Atlas and inventory visibility
Continuously expand a geographic island registry independently of NFT releases. Each island has two edition slots N/S, each independently shown as Unreleased, Available, Collected, or On Sale (minted with a verified active resale listing). Track release state separately from verified onchain mint/ownership and listing state; never infer availability from missing data. Atlas supports map and searchable list, region/country/name filters, edition status and complete-pair progress. All mint modes share the same released unminted inventory. Show eligible inventory sizes before blind/regional mint; direct mint allows available edition selection. Registry coverage must be reported honestly, not asserted exhaustive. Continuous release approved; three distinct mint prices desired, exact 250k/500k/750k KEY proposal awaiting approval.


## Island appreciation — Cheers to your Island
Add appreciation tipping directly to gallery cards and detail pages for minted editions, including collected and listed editions. Proposed presets 250 and 500 CHEERS, with 100% of the tip to the current verified NFT owner and no platform royalty on tips. Unminted editions do not receive tips. Resolve ownership at execution, prevent accidental self-tips, explicitly confirm recipient and amount; if ownership changes before execution, require renewed confirmation. Show confirmed per-edition cumulative tips separately from current owner receipts; do not count failed transactions. Verify CHEERS token contract, decimals and supported BaseFriend tipping interfaces before enabling payments; no assumptions about access to daily allowances or grant attribution. UI stays disabled until integration is verified. Gallery popularity rankings may follow, based on confirmed tips, not fabricated activity.

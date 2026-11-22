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


## In-app secondary transactions
Required creator fee on in-app resales: 10% of actual sale consideration, paid to 0xfc5708cb64604dcf6f62de5d63a051ed577e10c1. Direct NFT-for-NFT swaps also require a creator fee; approved basis is 10% of the undiscounted 500000 KEY mint price (50000 KEY per swap total), split equally: each participant pays 25000 KEY. Both payments and NFT transfers must settle atomically. CHEERS equivalent requires verified pricing. Settlement must be atomic, enforce fees in contract, and avoid double charging royalties. No deployed contract or active settlement yet.


## Canonical geographic scale policy
All islands receive equal visual prominence regardless of real area. Canonical canvas 2048 x 2048 px at 300 dpi; uniformly fit the longest projected bounding-box dimension to 1536 px (75% of canvas), center without stretching. Use a documented locally appropriate metric projection, record CRS, distortion limitations, projected extent, meters per pixel, true geographic area and orientation. Derive the scale bar from the actual artwork transform, and scale it responsively with the image. Display it outside the art in the app; no text or labels in the NFT artwork. Store nominal print scale at 300 dpi separately from digital meters per pixel. First candidate: Bouvetoya, Glacial Turquoise. Verified licensed coastline required before canonical art publication.

# Islands launch scope

User decision, 26 November 2026: prepare 500 islands for the initial launch,
with North-Up and South-Up artwork for each: 1,000 distinct artworks.
75 islands / 150 artworks are currently prepared; 425 islands / 850 artworks
remain to be produced and checked. This is a preparation target, not a new
onchain supply cap, claim that the works exist, or approval to activate minting.

Atlas is a map for geographic exploration, with markers linking to island
details. Index is the searchable geographic directory and availability list.
Gallery is the collection of verified minted editions. Only a wallet-verified
administrator session also includes unreleased prepared artwork in Gallery.

Farcaster wallet is the primary connection. The header exposes Administrator
as a sign-in entry; only the configured creator's verified signature unlocks
previews. Early Mini App detection is retried at connection time. Splash
readiness and host capability detection cannot indefinitely block the wallet.
Outside Farcaster, the connection dialog explains the context requirement and
links to the Mini App launcher; it does not pretend a public address lookup is
a wallet connection. Browser wallets remain an optional detected fallback.

The root page now includes Mini App launch embed metadata, and its previously
missing app icon is generated during the build along with a generic launch
preview. The manifest declares Base. Its accountAssociation is still absent:
linking this domain to the creator's Farcaster identity requires an authentic
signature in Farcaster's developer manifest tools. Do not fabricate this proof.
A live host connection and the creator's signature still require the user's
Farcaster session to validate end to end.

Previously published artwork URLs and share pages remain public files; the
administrator preview is a UI restriction, not private asset storage.

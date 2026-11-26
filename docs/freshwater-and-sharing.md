# Freshwater collection and artwork sharing

Added 26 existing artwork previews for islands 000051–000063, retaining the
original PNG bytes, metadata, N/S orientation, individual palettes and 26 distinct
background colors. The original package SHA-256 is
`383a3aff7b1c34b1a51a9c3a29a1725845a4f7953e4598a1cb9b86558a2b3e8d`.

Geographic configuration, coastline/water vectors, terrain validation, attribution
and the GSHHG license are available under
`public/drafts/freshwater-sources-20261126/`. Areas shown are approximate polygon
areas. This batch contains ten lake islands and three river islands. Existing
GeoNames aliases are excluded by their explicit source IDs to prevent duplicate
index entries; neighboring islands and unrelated islands with the same name remain.

Only island detail views offer Share on X and Share on Farcaster; gallery cards offer View island. All actions use the same bold Courier typeface as the artwork cards. X sharing opens the composer with
editable text and the chosen edition's `/share/000051-N.html` URL. Publishing is
performed by the visitor. No X credentials, account authorization or API access
are required by ISLANDS.

`scripts/build-share-pages.mjs` builds static HTML for all preview editions before
dev, test and production builds. Each page contains its own Open Graph and Twitter
image tags, an artwork preview and an app link using `?edition=000051-N`.
This query opens the correct island and highlights the requested orientation.
Static metadata can be fetched without executing the app's JavaScript. Actual
card rendering and caching are controlled by X and have not been verified in a
signed-in X composer.

The canonical production origin defaults to `https://islands-kappa.vercel.app`;
set `ISLANDS_PUBLIC_URL` if the production domain changes. Generated share pages
are build output and are excluded from git.

No mint inventory, public mint function, KEY payment or staking eligibility was
activated by this gallery update. All artwork remains clearly marked as previews.

## Artwork and NFT status

The index keeps its name-and-status list: Exists / Not existing refers to the
artwork, independently of mint status. Gallery cards show Exists · Not minted for
the current unreleased previews. Each North-Up/South-Up detail has a separate
record for Artwork, Mint, Minted by and Owned by. Country / territory remains in
the geography section so it cannot be confused with NFT ownership.

The collection is explicitly unreleased. No minter or current owner is invented;
those fields display an em dash until issuance. `edition-status.js` can format
verified chain snapshots, keeping the original minter separate from the current
holder, and returns Not verified for missing data on a released collection. It
does not fetch ownership data itself. A verified onchain reader and released
collection configuration must be connected before enabling production minting.

## Farcaster sharing and compact traits

Each edition detail offers Share on Farcaster. Inside a Farcaster Mini App it
opens the native `sdk.actions.composeCast` composer with the edition name,
orientation, palette and a single edition-specific share-page embed. Cancellation
does not open another composer. If the native action errors, the Farcaster web
composer is offered via `openUrl`; a regular browser uses the same composer URL
directly. The visitor chooses whether to publish.

All 150 share pages now expose `fc:miniapp` and legacy `fc:frame` metadata. Their
1200x800 PNG preview centers the full square original without cropping it, and
the launch action points to the exact N/S edition in the app. Generated preview
images are build output. The automated checks verify composer text/encoding,
per-edition launch URLs and image dimensions. Native client rendering and
publication require a real Farcaster session and have not been verified here.

Trait label/value pairs remain in two columns; the vertical row gap is reduced
from 14px to 5px, while long values can wrap.

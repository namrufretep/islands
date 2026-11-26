# Islands index and creator preview — 26 November 2026

The index now groups existing artworks first for every initial, search, status
filter and sort direction. Within each group, island names or countries sort in
the chosen A–Z or Z–A direction. Equal country names use the same island-name
ordering. Leading apostrophes and accents do not create separate letter groups.

## Wallet-bound administrator preview

Connect the creator wallet `0xfc5708cb64604dcf6f62de5d63a051ed577e10c1`.
The header then offers **Administrator view**. Activation requests a personal
message signature scoped to the current origin, nonce and a thirty-minute
expiry. It requests no transaction, token approval or transfer. The signature
must verify for the creator address; a typed address in the Keys lookup field
cannot activate it. Verification supports EOA and smart-account signatures via
Viem's public-client verifier on Base.

The session stays in memory. Switching accounts or chains, disconnecting,
expiry, reload, or choosing **Exit administrator view** removes the preview.
The creator sees all 150 North/South artwork previews, including those not
minted. Public gallery and island pages show a question mark for unreleased
artwork and omit palette and background traits from their visible details.

This is a wallet-verified interface preference, **not private file storage**.
Previously published originals, thumbnails, metadata and crawler share images
remain accessible by their URLs. Strong pre-mint secrecy requires moving those
assets behind authenticated server delivery and changing share-image generation.
No NFT collection deployment or mint-state verification is implied by this work.

## Full registry audit

Every one of the 166,980 GeoNames source records was checked programmatically.
Source IDs and original source data remain intact. A separate review manifest
suppresses 70 close records with the same normalized name and country on the
same GSHHG shoreline polygon, with a maximum 200-metre point separation.
The geographically matched curated aliases are also folded into curated rows.
Broad two-degree proximity suppression has been removed.

The two **Baboon Island** entries in the screenshot are distinct gazetteer
locations in Guyana, about 210 km apart (`3379591` and `3661405`). They remain
separate, with country and coordinates shown under the name. Names shared by
other locations are similarly disambiguated instead of deleted by spelling.

The original import contained name, country code, coordinates and source ID;
it did not contain area, settlement or administrative-region fields. The
island detail view now uses its known registry country, including for entries
outside the curated artwork collection. It no longer substitutes a different
same-named curated island's country or area. There are 44 source records without
a country code; these remain explicitly unrecorded.

## Area coverage and limits

31,818 source entries have a published approximate GSHHG polygon-area match.
The full-resolution audit records **46,758** unique shoreline matches, with **14,879** withheld because multiple
island names occur in one polygon; duplicate suppression explains the remaining
coverage difference. **120,222** points have no unique eligible shoreline match.
The 83 curated registry entries were also checked: 82 have artwork-geometry or
GSHHG estimates in the review manifest; Île de la Cité remains unresolved there.
Existing manually curated reference areas take priority in the interface.

No mainland areas are assigned to island points. When multiple names fall in
one shoreline polygon, the whole polygon's area is withheld to avoid assigning
a larger landmass to a small or imprecisely located island. GSHHG version 2.3.7
is a 2017 shoreline database; these are approximate polygon areas, not surveyed
or current cadastral land areas. Lake-island matches can additionally identify
freshwater; coastal level-one matches do not imply ocean salinity.

Area detail data is split into 32 small files and loaded only when needed.
Remaining areas, settlements and regions need additional sourced research;
they have not been filled with guesses. This audit does not constitute manual
geographic verification of every gazetteer entry.

Sources: [GeoNames](https://www.geonames.org/) (CC BY 4.0),
[GSHHG 2.3.7](https://www.soest.hawaii.edu/wessel/gshhg/) by Wessel and Smith
(LGPL 3 or later; licensing notices retained under public/drafts/*-sources-*).
The reproducible enrichment script is `scripts/enrich_island_index.py` and the
machine-readable counts and duplicate groups are in `docs/index-data-review.json`.

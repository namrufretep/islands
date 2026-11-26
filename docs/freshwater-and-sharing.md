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

Gallery cards and island details offer Share on X. This opens the X composer with
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

# ISLANDS — Trait schema v1.0

Proposed implementation schema, pending metadata migration and geographic review. One geographic Island ID, distinct Artwork IDs for N/S, independent contract token IDs.

## Geographic traits
Island ID; Artwork ID; Island; Country (sovereign jurisdiction, multiple values where applicable; disputed claims explicitly qualified); Region (geographic region, not continent); Island Type (Ocean Island, Sea Island, Lake Island, River Island, Estuarine Island, other as needed); Water Type (Saltwater, Freshwater, Brackish Water, Mixed, as verified); Ocean (optional, geographically applicable); Water Body (named immediate surrounding water, multiple where applicable); Area (km², numeric main-island area from source geometry); Scale (artwork print scale at 300 dpi); Largest Settlement (verified, omit if unknown; Uninhabited only when verified).

## Artistic traits
Orientation (North-Up/South-Up); Color Palette (individual named palette); Color Family (controlled broad color category); Background (individual named background).

Soft Stone is the collection-wide artistic identity, not an NFT attribute. Keep the surface model in technical metadata only.

Keep exact palette hex stops, background hex, rendering version, surface model, geographic sources, projection and licensing review in technical metadata. Do not infer water salinity solely from island type. Omit inapplicable or unknown traits rather than invent values. Preserve artwork and IDs during metadata migration. NFT attributes use trait_type/value entries; numeric area remains numeric. Existing draft JSONs are not yet migrated. Country and water body assignments require geographic verification before release.

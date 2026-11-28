# A–Z Islands VI · Changing Light · 000231–000256

26 new geographic islands, one per initial A–Z. 52 independent North-Up/South-Up originals at 2048×2048 pixels, nominal 300 dpi. The prepared collection now contains 256 islands / 512 editions toward the 500-island launch target. These are unreleased artwork previews, not minted NFTs.

A Andros · B Belle-Île · C Corfu · D D’Urville Island · E Eday · F Folegandros · G Grímsey · H Hvar · I Inishbofin · J Jindo · K Kalymnos · L La Palma · M Maui · N Nusa Penida · O Ons · P Paros · Q Qamea · R Rab · S Skye · T Taveuni · U Upolu · V Vega · W Wight · X Xiyang Dao · Y Yashiro-jima · Z Zamami

## Artwork

Preserves the original Bouvetøya-inspired continuous Soft Stone surface (4.7-bouvet-directional), four-colour mineral ramps and 85% canvas footprint. No text, political borders, contour lines or stepped relief. Per-edition light azimuths cover eight directions, with elevation 35–55°. Each pair has different palettes, backgrounds and light directions. Backgrounds span light and dark colours. The same light source drives the relief, coastal shading, background wash and opposite soft cast shadow. South-Up lighting is calculated for its final screen orientation. Artistic relief is an interpretation of the elevation source, not a literal geological model.

## Geography and qualifications

GSHHG 2.3.7 full-resolution L1 physical coastlines; public Mapzen elevation tiles; GeoNames names, stable identifiers and qualified settlement evidence. Every reference point was inside exactly one valid physical island polygon. New polygons were checked against each other and 156 available prior coastline source files for duplicate coverage. Taveuni includes both antimeridian-split physical parts; its displayed 434 km² land area follows the Fiji Ministry of Tourism and Civil Aviation (2023), https://mcttt.gov.fj/wp-content/uploads/2023/10/TDPVL_SESA_TOR_Oct19.pdf, p. 2. The larger GSHHG polygon estimate is retained separately. Other areas are approximate WGS84 geodesic polygon areas of the GSHHG dataset and may differ from current surveyed land area.

D’Urville is the New Zealand island, not Antarctica. Inishbofin is the Connemara island in County Galway, not County Donegal. Grímsey is the Arctic Circle island north of Iceland. Wight is the short display name of England's Isle of Wight. Additional GeoNames aliases for D’Urville, Jindo and Skye are suppressed in the index to avoid duplicate entries.

Inland waters are the non-exhaustive GSHHG L2 baseline. Supplemental OSM requests were unavailable or rate limited on 2026-11-28; zero mapped-water polygons must not be interpreted as proof that an island has no lakes. Settlement names are the highest recorded population among GeoNames cities500 points contained by the physical shoreline. This is gazetteer evidence, not an exhaustive census; unsupported entries remain null.

## Reproduce from the repository root

```sh
python3 -B scripts/prepare_alphabet_geography.py --source-dir /path/to/gshhg --cities /path/to/cities500.zip --source data/collections/alphabet-000231-000256
python3 -B scripts/render_african_collection.py --cache /path/to/terrain-cache --source data/collections/alphabet-000231-000256 --edition-dir bouvet-light-20261128-vi --style bouvet-original --variable-lighting
python3 -B scripts/register_alphabet_collection.py --source data/collections/alphabet-000231-000256 --edition-dir bouvet-light-20261128-vi
python3 -B scripts/export_alphabet_collection.py --output /path/to/export --source data/collections/alphabet-000231-000256 --edition-dir bouvet-light-20261128-vi --name Islands_000231-000256_Changing_Light_A-Z
python3 -B scripts/test_island_lighting.py
```

Coastline attribution: GSHHG / Wessel and Smith, LGPL-3.0-or-later. Gazetteer attribution: GeoNames CC BY 4.0. Terrain source URLs and coverage checks are retained in each edition's metadata.

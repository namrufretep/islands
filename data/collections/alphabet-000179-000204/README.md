# A–Z Islands IV · Bouvet · 000179–000204

26 additional physical islands, one for every initial A–Z, with 52 individually coloured North-Up/South-Up originals at 2048×2048 pixels and nominal 300 dpi. This extends the preceding 178 islands to 204 geographic islands / 408 artwork editions.

A Arran · B Brač · C Culebra · D Dønna · E Espiritu Santo · F Formentera · G Gaua · H Hiddensee · I Inishmore · J Jost Van Dyke · K Ko Samui · L Leros · M Miyajima · N Navarino · O Ocracoke · P Procida · Q Quinchao · R Raiatea · S Sark · T Tilos · U Ugljan · V Viti Levu · W Waiheke Island · X Xiaoliuqiu · Y Yakushima · Z Zanzibar (Unguja).

## Bouvet art direction

The user's reference is the original Bouvetøya artwork, geographic ID 000001, art version 3.8. This batch uses a distinct `bouvet-original` rendering mode, version 4.6-bouvet. Its broad continuous lighting field follows the original reference's coast-distance dome, heavily smoothed elevation, and fixed upper-left light. The dome and artistic height are normalized to artwork space so small and large islands receive comparable visual softness. The full four-colour palette is blended continuously; the reference's broad tonal washes replace the preceding mode's narrow rim and elevation-colour mixture. Each South-Up edition rotates the geographic geometry and recomputes directional illumination. The exact source silhouette is rasterized independently at 2048 pixels. No terrace steps, separating lines or text are added to the artwork. A restrained close shadow uses 8% maximum opacity.

There are 52 distinct background values, with both pale mineral fields and deep slate, moss, plum, petrol and graphite combinations. Each edition retains its own palette and background; the common reference concerns surface and light rather than using one colour for every island.

## Geographic evidence and limits

Coastlines: GSHHG 2.3.7 full-resolution L1 physical shorelines, Wessel and Smith, LGPL-3.0-or-later. Names and geographic IDs: GeoNames, CC BY 4.0. Whole-island terrain: public Mapzen elevation tiles, with source URLs and measured land coverage retained per edition. Every reference point was checked inside a valid physical shoreline; all new outlines were checked for duplicate coverage against earlier available source outlines. Additional same-island GeoNames IDs for Viti Levu and Waiheke were checked inside their physical shorelines and suppressed as curated aliases.

Miyajima is the island also called Itsukushima; its display name is supported by the Japan National Tourism Organization: https://www.japan.travel/en/destinations/chugoku/hiroshima/miyajima/ . Xiaoliuqiu is GeoNames Liuqiu Yu; the Dapeng Bay National Scenic Area identifies the island: https://www.dbnsa.gov.tw/en/attraction/AttractionAreaPage?a=142 . Zanzibar here is the physical island Unguja, not the entire archipelago or region.

Areas are approximate WGS84 geodesic areas of the 2017 physical shoreline polygons, not current surveyed areas. Small and tidal islands may have limited shoreline detail or differ from current land areas. Inland waters are the non-exhaustive GSHHG L2 baseline. Supplemental OSM services were unavailable on 2026-11-28. A zero mapped-water count does not mean an island has no lakes. Relief is an artistic interpretation of elevation.

Settlement evidence is the highest population among GeoNames cities500 points contained by the physical shoreline. It is qualified gazetteer evidence, not an exhaustive census; administrative localities and municipal subdivisions can appear in that data. Missing evidence stays null. Original source records and these qualifications are retained per island.

## Reproduce

From the repository root, after extracting GSHHG full-resolution shapefiles and obtaining the GeoNames cities500 archive:

```sh
python3 scripts/prepare_alphabet_geography.py --source-dir /path/to/gshhg --cities /path/to/cities500.zip --source data/collections/alphabet-000179-000204
python3 scripts/render_african_collection.py --cache /path/to/terrain-cache --source data/collections/alphabet-000179-000204 --edition-dir bouvet-20261128-iv --style bouvet-original
python3 scripts/register_alphabet_collection.py --source data/collections/alphabet-000179-000204 --edition-dir bouvet-20261128-iv
python3 scripts/export_alphabet_collection.py --output /path/to/export --source data/collections/alphabet-000179-000204 --edition-dir bouvet-20261128-iv --name Islands_000179-000204_Bouvet_A-Z
```

Registration exposes these unreleased previews in the existing administrator/Atlas flows. It does not mint or release tokens; the public gallery follows verified mint state.

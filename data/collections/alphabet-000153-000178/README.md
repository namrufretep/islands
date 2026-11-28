# A–Z Islands III · 000153–000178

26 additional physical islands, one per initial A–Z. Each island has two separately coloured and lit North-Up/South-Up editions: 52 original 2048×2048 PNG files at nominal 300 dpi. This batch extends the previous 152 islands.

A Anticosti · B Borkum · C Cres · D Dugi Otok · E El Hierro · F Faial · G Guernsey · H Hachijō-jima · I Ikaria · J Jersey · K Kangaroo Island · L Lifou · M Milos · N Norderney · O Ouessant · P Pantelleria · Q Qeqertarsuaq · R Rügen · S São Jorge · T Tobago · U Unst · V Værøy · W Whidbey Island · X Xi Dao · Y Yttygran · Z Zembra.

## Geographic evidence

Physical shorelines use GSHHG 2.3.7 full-resolution L1, Wessel and Smith, LGPL-3.0-or-later. Names, stable geographic IDs, reference coordinates and qualified settlement evidence use GeoNames, CC BY 4.0. Every reference point lies inside exactly one valid physical shoreline; country polygons are never used. Each new shoreline was also checked for duplicate physical coverage against the prior available source outlines. Qeqertarsuaq here means Disko Island (GeoNames 3420645), not the settlement or another same-named island. Xi Dao is the small island off Sanya, Hainan.

Areas are approximate WGS84 geodesic polygon areas of the 2017 shoreline dataset. They may differ from current surveyed areas, particularly on tidal or reclaimed coasts. Inland waters use the GSHHG L2 baseline. Supplemental OpenStreetMap queries were unavailable on 2026-11-28; the water layer is not exhaustive. A zero water count does not establish that an island has no lakes. No missing lakes have been invented.

Settlement entries are the highest recorded population among the GeoNames cities500 points contained by the physical shoreline, not an independently exhaustive population census. A locality or municipal subdivision may be returned instead of a commonly used larger settlement name; the source record is retained. Unsupported entries remain null.

## Artwork

The established Soft Stone renderer uses a locally centered azimuthal-equidistant projection, a physical silhouette rasterized at 2048 pixels, and whole-island public Mapzen elevation resampled at 512 pixels. The longest island dimension occupies 85% of the canvas. Elevation is artistically smoothed into continuous rounded mineral relief. North-Up and South-Up have different palettes, backgrounds and recalculated upper-left lighting. There are 52 separate background values, emphasizing midnight blue, petrol, spruce, aubergine and charcoal alongside lighter mineral combinations. Tile sources, land coverage, scale, orientation and image hashes are recorded per edition.

## Reproduce

From the repository root, with the extracted GSHHG full-resolution shapefiles and the GeoNames cities500 archive:

```sh
python3 scripts/prepare_alphabet_geography.py --source-dir /path/to/gshhg --cities /path/to/cities500.zip --source data/collections/alphabet-000153-000178
python3 scripts/render_african_collection.py --cache /path/to/terrain-cache --source data/collections/alphabet-000153-000178 --edition-dir alphabet-20261128-iii
python3 scripts/register_alphabet_collection.py --source data/collections/alphabet-000153-000178 --edition-dir alphabet-20261128-iii
python3 scripts/export_alphabet_collection.py --output /path/to/export --source data/collections/alphabet-000153-000178 --edition-dir alphabet-20261128-iii --name Islands_000153-000178_A-Z
```

Registration makes these previews available to the existing administrator and Atlas flows. It does not mint or release an NFT. The public gallery continues to show verified minted editions.

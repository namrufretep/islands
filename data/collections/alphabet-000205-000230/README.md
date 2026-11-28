# A–Z Islands V · Changing Light · 000205–000230

26 new geographic islands, one per initial A–Z, with 52 independently coloured and illuminated North-Up/South-Up originals at 2048×2048 pixels, nominal 300 dpi. This extends the preceding 204 islands to 230 islands / 460 editions.

A Ambon · B Bute · C Camiguin · D Dinagat · E Erromango · F Futuna · G Gozo · H Hitra · I Ischia · J Jura · K Kos · L Langkawi · M Maupiti · N Nuku Hiva · O Ovalau · P Pemba · Q Quirpon Island · R Raasay · S Savai‘i · T Terceira · U Utila · V Ventotene · W Wetar · X Xiaodeng Dao · Y Yasawa · Z Zhoushan.

## Art and lighting

The user requested the soft broad surface of the original Bouvetøya reference with varied light and shadow directions. Version 4.7-bouvet-directional retains the established `bouvet-original` surface and adds per-edition lighting design. Light azimuth is measured clockwise from screen top: 0° top, 90° right, 180° bottom, 270° left, plus the four diagonals. All eight directions occur in this batch. Elevations vary from 35° to 55°. Each island's N/S pair uses distinct screen-space light directions, separated by 90°, 135° or 180°.

The same light vector drives the main relief, restrained coastal shading, the background wash and the opposite cast-shadow offset. South-Up lighting is computed in the rotated artwork's screen coordinates. The soft close shadow remains at 8% maximum opacity and varies in offset with light direction and elevation. Each edition records the azimuth convention, elevation, screen direction, horizontal light vector and actual shadow pixel offset. These are artwork provenance fields; no extra NFT trait has been introduced.

Continuous four-colour mineral ramps, broad dome/elevation-guided shading and the 85% canvas footprint are preserved. The physical silhouette is rasterized independently at 2048 pixels. The 52 backgrounds are distinct; palettes and orientations are independently designed. The artistic relief is not a literal geological model.

## Geographic evidence and limitations

Physical coastlines: GSHHG 2.3.7 full-resolution L1, Wessel and Smith, LGPL-3.0-or-later. Geographic names, stable IDs and qualified settlement points: GeoNames CC BY 4.0. Whole-island terrain: public Mapzen elevation tiles; source URLs and measured land coverage are retained per edition. Each reference point was checked inside exactly one valid physical island outline. New outlines were checked against previous available source outlines and one another for duplicate physical coverage. Camiguin means the island near northern Mindanao, not the same-named island in the Babuyan group. Futuna means the island in Wallis and Futuna. Maupiti here is the central physical island, not the surrounding lagoon and motu.

Areas are approximate WGS84 geodesic areas of the 2017 coastline polygons, not current surveyed land areas. Small/tidal shorelines may have limited detail, and later reclamation or erosion can change coastlines. Inland waters are the non-exhaustive GSHHG L2 baseline. Supplemental OSM service requests were unavailable on 2026-11-28. A zero mapped-water count does not establish that an island has no lakes.

Settlement entries are the highest recorded population among GeoNames cities500 points contained by the shoreline. This is qualified gazetteer evidence, not an exhaustive census; whole-island localities and municipal subdivisions can appear. Unsupported entries remain null. Source records and qualifications are retained in the metadata.

## Reproduce

From the repository root, with the extracted GSHHG full-resolution shapefiles and GeoNames cities500 archive:

```sh
python3 -B scripts/prepare_alphabet_geography.py --source-dir /path/to/gshhg --cities /path/to/cities500.zip --source data/collections/alphabet-000205-000230
python3 -B scripts/render_african_collection.py --cache /path/to/terrain-cache --source data/collections/alphabet-000205-000230 --edition-dir bouvet-light-20261128-v --style bouvet-original --variable-lighting
python3 -B scripts/register_alphabet_collection.py --source data/collections/alphabet-000205-000230 --edition-dir bouvet-light-20261128-v
python3 -B scripts/export_alphabet_collection.py --output /path/to/export --source data/collections/alphabet-000205-000230 --edition-dir bouvet-light-20261128-v --name Islands_000205-000230_Changing_Light_A-Z
python3 -B scripts/test_island_lighting.py
```

Registration includes these unreleased previews in the existing administrator/Atlas flows. It does not mint or release NFTs. Public gallery visibility continues to follow verified mint state.

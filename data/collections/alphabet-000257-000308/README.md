# Chromatic Islands · 000257–000308

52 new geographic islands, two A–Z cycles, 104 independent North-Up/South-Up original artwork previews at 2048×2048 pixels and nominal 300 dpi. Prepared collection total: 308 islands / 616 editions toward the 500-island target. These previews do not mint or release NFTs.

## Colour and surface

The user explicitly requested more than four colours and less repetitive, less conventional combinations for the next 52 islands. Version 4.8-bouvet-chromatic uses 7, 8, 9 or 10 colour stops per edition. Eight distinct saturation/lightness profiles range from electric contrasts through smoky pigments, dark iridescence, pale chromatic stone, oxidised accents, ink/acid, jewel colour and mist/fluorescence. Every one of the 104 editions has a unique palette, a unique three-family hue combination and a unique background. Palette colour placement is independent of the light source: it combines a broad spatial field with smoothed terrain and coastline distance. Four field arrangements are used: sweeping, crossflow, confluence and halo. Quantile normalization spreads each palette across the island surface instead of losing most colours in a small part of the tonal range. Smooth interpolation and continuous fields preserve soft transitions; no contour bands or hard colour boundaries are introduced.

Directional light remains linked to the elevation-guided sculptural surface and cast shadow, with eight azimuths and elevations 35–57 degrees. New colour fields are artistic choices, not geological or land-cover classifications. The geographic silhouette, 85% canvas footprint, broad Bouvet-inspired surface and independent 180° South-Up orientation are retained. Existing artworks have not been recoloured.

## Geography

Physical shoreline: GSHHG 2.3.7 full-resolution L1. Terrain: public Mapzen elevation tiles, with source URLs and land-coverage checks in metadata. Names, stable identifiers and qualified settlement evidence: GeoNames. All 52 source shapes were checked against each other and 182 available previous source shapes to exclude duplicate physical islands. Areas are approximate geodesic GSHHG polygon areas. Gazetteer settlement names are qualified evidence from contained cities500 points, not an exhaustive census. Unsupported settlement names remain null.

Wrangel Island and any other dateline-crossing shape include touching physical shoreline pieces from both sides of the antimeridian. Terrain tiles on the two sides are reprojected separately, avoiding a world-wide Mercator mosaic. Xiji Yu's GeoNames point lies about 110 m off the GSHHG coast; a representative point inside the nearest approximately 1 km² polygon is used, with the original gazetteer coordinates retained.

Udo is east of Jeju. Flinders Island is the Furneaux Group island in Tasmania. Damar is in Maluku. Flores (Indonesia) is separate from Flores (Azores), already in the collection. Vanua Levu is Fiji's large northern island, not the small same-named Mamanuca island. Uvea (Wallis) and Ouvéa (New Caledonia) are distinct geographic islands. Zirje is the ASCII display form of Žirje. The second Rebun GeoNames identifier is suppressed as an index alias.

Inland waters are the non-exhaustive GSHHG L2 baseline. A zero mapped-water count does not establish that an island has no lakes. Reef and tidal outlines in small-island source polygons can differ from newer surveyed shorelines.

## Included islands

000257 · A · Atiu · Cook Islands
000258 · B · Bioko · Equatorial Guinea
000259 · C · Chios · Greece
000260 · D · Dassen Island · South Africa
000261 · E · Elba · Italy
000262 · F · Flinders Island · Australia
000263 · G · Great Barrier Island · New Zealand
000264 · H · Hainan · China
000265 · I · Ishigaki · Japan
000266 · J · Juan de Nova · French Southern Territories
000267 · K · Kythira · Greece
000268 · L · Lord Howe Island · Australia
000269 · M · Moloka‘i · United States
000270 · N · Nantucket · United States
000271 · O · Olib · Croatia
000272 · P · Palawan · Philippines
000273 · Q · Quirimba · Mozambique
000274 · R · Rote · Indonesia
000275 · S · San Cristóbal · Ecuador
000276 · T · Thassos · Greece
000277 · U · Udo · South Korea
000278 · V · Vanua Levu · Fiji
000279 · W · Wrangel Island · Russia
000280 · X · Xiji Yu · Taiwan
000281 · Y · Yapen · Indonesia
000282 · Z · Zirje · Croatia
000283 · A · Aguni · Japan
000284 · B · Bintan · Indonesia
000285 · C · Cozumel · Mexico
000286 · D · Damar · Indonesia
000287 · E · Euboea · Greece
000288 · F · Flores (Indonesia) · Indonesia
000289 · G · Grande Comore · Comoros
000290 · H · Herm · Guernsey
000291 · I · Iriomote · Japan
000292 · J · Jicarón · Panama
000293 · K · Koh Rong · Cambodia
000294 · L · Lombok · Indonesia
000295 · M · Martinique · Martinique
000296 · N · Negros · Philippines
000297 · O · Ouvéa · New Caledonia
000298 · P · Ponza · Italy
000299 · Q · Quiriquina · Chile
000300 · R · Rebun · Japan
000301 · S · Sumba · Indonesia
000302 · T · Terschelling · Netherlands
000303 · U · Uvea (Wallis) · Wallis and Futuna
000304 · V · Vannøya · Norway
000305 · W · Westray · United Kingdom
000306 · X · Xiaochangshan Dao · China
000307 · Y · Yonaguni · Japan
000308 · Z · Zmajan · Croatia

## Reproduce from the repository root

```sh
python3 -B scripts/prepare_alphabet_geography.py --source-dir /path/to/gshhg --cities /path/to/cities500.zip --source data/collections/chromatic-000257-000308
python3 -B scripts/render_african_collection.py --cache /path/to/terrain-cache --source data/collections/chromatic-000257-000308 --edition-dir chromatic-20261128-final --style bouvet-original --variable-lighting
python3 -B scripts/register_alphabet_collection.py --source data/collections/chromatic-000257-000308 --edition-dir chromatic-20261128-final
python3 -B scripts/export_alphabet_collection.py --output /path/to/export --source data/collections/chromatic-000257-000308 --edition-dir chromatic-20261128-final --name Islands_000257-000308_Chromatic_A-Z
python3 -B scripts/test_chromatic_surface.py
python3 -B scripts/test_island_lighting.py
```

Attribution: GSHHG / Wessel and Smith, LGPL-3.0-or-later; GeoNames CC BY 4.0; Mapzen elevation tiles.

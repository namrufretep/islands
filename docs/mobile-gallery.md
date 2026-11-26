# Mobile gallery memory reduction

The reported iPhone browser error occurs during enlargement. The screenshot alone
does not establish an exact crash cause. The code had several avoidable memory
costs: 126 full-resolution gallery images, large transformed/masked decorative
layers, and a 19 MB global island index fetched while visiting the gallery.

The gallery now displays at most 24 generated 640px WebP thumbnails per page.
All 126 editions remain searchable and accessible through pagination. The original
2048px PNGs remain unchanged and are loaded individually in an accessible modal
image viewer, with a direct original-image link. Closing the viewer clears its
image source and restores scrolling. Browser pinch zoom is not disabled.

The global island index is requested only when the visitor opens Index. Its
request is guarded against duplicate concurrent fetches. Decorative background
grids are drawn directly inside the viewport; the oversized transformed/masked
layers were removed, and decorative page SVGs are limited to 1400 CSS pixels.

Thumbnails are generated before dev, test and production builds with Sharp.
Generated files are ignored by git. Original image integrity and thumbnail
dimensions are covered by the existing artwork checks and thumbnail test.

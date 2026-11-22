import json, hashlib
from pathlib import Path
from shapely.geometry import shape, Point
from pyproj import Geod
import numpy as np
base=Path('data/gis/000001')
stem=base/'coastline/000001-candidate-00'
m=json.loads(stem.with_suffix('.json').read_text())
g=shape(json.loads(stem.with_suffix('.geojson').read_text()))
assert m['layer']=='B20_Land_f.shp'
assert g.is_valid and g.geom_type=='Polygon' and g.covers(Point(3.36,-54.42))
assert 48<abs(Geod(ellps='WGS84').geometry_area_perimeter(g)[0])/1e6<51
t=json.loads((base/'terrain/terrain-00.json').read_text())
assert t['crs']==m['projection']
with np.load(base/'terrain/terrain-00.npz') as raster:
    assert list(raster['elevation'].shape)==t['shape']
    assert np.nanmax(raster['elevation'])>700
m.update(status='verified_coastline',svg_sha256=hashlib.sha256(stem.with_suffix('.svg').read_bytes()).hexdigest(),verification='Automated land layer, topology, reference point and area checks; visual review pending',attribution='Norwegian Polar Institute, B20 Kartdata; verify license before release')
Path('review-output').mkdir(exist_ok=True)
Path('review-output/coastline.json').write_text(json.dumps(m,indent=2))

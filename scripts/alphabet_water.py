"""Fetch bounded OSM inland-water outlines, then apply them after terrain rendering.
Fetch and apply are separate to avoid changing source geometry during a render.
"""
import argparse,json,urllib.request,urllib.parse,urllib.error,threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from shapely.geometry import shape,Polygon,LineString,mapping
from shapely.ops import polygonize,unary_union
stop=threading.Event()
p=argparse.ArgumentParser();p.add_argument('mode',choices=['fetch','apply']);a=p.parse_args()
source=Path('data/collections/alphabet-000101-000126');configs=json.loads((source/'geography-validation.json').read_text());cache=source/'osm-water';cache.mkdir(exist_ok=True)
def geometry(e):
 if e['type']=='way':
  points=[(p['lon'],p['lat']) for p in e.get('geometry',[]) if 'lon' in p]
  return Polygon(points) if len(points)>3 and points[0]==points[-1] else None
 if e['type']=='relation':
  lines={role:[] for role in ['outer','inner']}
  for member in e.get('members',[]):
   pts=[(p['lon'],p['lat']) for p in member.get('geometry',[]) if 'lon' in p]
   if len(pts)>1:lines['inner' if member.get('role')=='inner' else 'outer'].append(LineString(pts))
  if not lines['outer']:return None
  outer=unary_union(list(polygonize(unary_union(lines['outer']))))
  return outer.difference(unary_union(list(polygonize(unary_union(lines['inner']))))) if lines['inner'] else outer
 return None
def fetch(c):
 if stop.is_set():return
 target=cache/(c['id']+'.json')
 if target.exists():return
 g=shape(json.loads((source/(c['id']+'-'+c['slug']+'-coastline.geojson')).read_text()));w,s,e,n=g.bounds
 q=f'[out:json][timeout:40];nwr["natural"="water"]({s},{w},{n},{e});out geom;'
 request=urllib.request.Request('https://overpass-api.de/api/interpreter?'+urllib.parse.urlencode({'data':q}),headers={'User-Agent':'ISLANDS-Geography/1.0'})
 try:
  with urllib.request.urlopen(request,timeout=20) as r:data=r.read(15_000_001)
  if len(data)>15_000_000:raise ValueError('Water response too large')
  j=json.loads(data)
  if 'remark' in j:raise ValueError(j['remark'])
  target.write_bytes(data);print(c['name'],len(j.get('elements',[])),'water candidates',flush=True)
 except urllib.error.HTTPError as error:
  if error.code==429:stop.set()
  print(c['name'],'water fetch unavailable:',error,flush=True)
 except Exception as error:print(c['name'],'water fetch unavailable:',error,flush=True)
if a.mode=='fetch':
 with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(fetch,configs))
else:
 for c in configs:
  target=cache/(c['id']+'.json')
  if not target.exists():continue
  prefix=c['id']+'-'+c['slug'];coast=shape(json.loads((source/(prefix+'-coastline.geojson')).read_text()));water=shape(json.loads((source/(prefix+'-water.geojson')).read_text()));parts=[] if water.is_empty else [water];urls=[]
  for item in json.loads(target.read_text()).get('elements',[]):
   g=geometry(item)
   if g is None or g.is_empty or not g.is_valid or g.area>coast.area*.3:continue
   if coast.covers(g.representative_point()):
    clipped=g.intersection(coast)
    if not clipped.is_empty and clipped.geom_type in ['Polygon','MultiPolygon']:parts.append(clipped);urls.append(f'https://www.openstreetmap.org/{item["type"]}/{item["id"]}')
  water=unary_union(parts);(source/(prefix+'-water.geojson')).write_text(json.dumps(mapping(water),separators=(',',':'))+'\n')
  c['water_sources']=list(dict.fromkeys(c['water_sources']+urls));c['water_count']=len(water.geoms) if hasattr(water,'geoms') else 0 if water.is_empty else 1
  c['water_note']='Mapped inland waters from GSHHG and a dated OpenStreetMap query; not exhaustive.'
  (source/(prefix+'.json')).write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n');print(c['name'],c['water_count'],'mapped water polygons',flush=True)
 (source/'geography-validation.json').write_text(json.dumps(configs,ensure_ascii=False,indent=2)+'\n')

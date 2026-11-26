"""Fetch physical island outlines and cross-check them with GSHHG 2.3.7.

Run with --source-dir pointing to an extracted GSHHG shapefile distribution.
Administrative boundaries are never used as island outlines.
"""
import argparse,json,hashlib,urllib.request,urllib.parse,time,unicodedata
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
from shapely.geometry import Point,Polygon,LineString,mapping,shape
from shapely.ops import polygonize,unary_union
from pyproj import Geod

p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--cached-only',action='store_true');a=p.parse_args()
configs=json.loads(Path('data/collections/africa-000064-000075.json').read_text())
cache=a.source_dir/'overpass';cache.mkdir(exist_ok=True)
out=Path('public/drafts/africa-sources-20261126');out.mkdir(parents=True,exist_ok=True)
geod=Geod(ellps='WGS84')
area=lambda g:abs(geod.geometry_area_perimeter(g)[0])/1e6
def fetch(c):
 target=cache/(c['slug']+'.json')
 if not target.exists():
  if a.cached_only:return c,None
  lon,lat=c['reference']
  q=f'[out:json][timeout:90];(nwr["place"="island"](around:6000,{lat},{lon}););out geom;'
  req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'IslandsGeographyReview/1.0'})
  try:
   with urllib.request.urlopen(req,timeout=110) as response:data=response.read(12_000_001)
   if len(data)>12_000_000:raise ValueError('Overpass response exceeds bound')
   parsed=json.loads(data)
   if 'remark' in parsed:raise RuntimeError(parsed['remark'])
   target.write_bytes(data)
  except Exception as error:
   print(c['name'],'OSM unavailable:',error,flush=True);return c,None
 return c,json.loads(target.read_text())
def geometry(element):
 if element['type']=='way':
  pts=[(x['lon'],x['lat']) for x in element.get('geometry',[]) if 'lon' in x]
  return Polygon(pts) if len(pts)>3 and pts[0]==pts[-1] else None
 if element['type']=='relation':
  outers=[];inners=[]
  for member in element.get('members',[]):
   pts=[(x['lon'],x['lat']) for x in member.get('geometry',[]) if 'lon' in x]
   if len(pts)>1:(inners if member.get('role')=='inner' else outers).append(LineString(pts))
  if not outers:return None
  parts=list(polygonize(unary_union(outers)))
  if not parts:return None
  outer=unary_union(parts)
  if inners:outer=outer.difference(unary_union(list(polygonize(unary_union(inners)))))
  return outer
 return None
results=[]
with ThreadPoolExecutor(max_workers=2) as pool:
 fetched=list(pool.map(fetch,configs))
for c,data in fetched:
 lon,lat=c['reference'];ref=Point(lon,lat);level=3 if c['water_type']=='Freshwater' else 1
 gsfile=a.source_dir/'GSHHS_shp/f'/f'GSHHS_f_L{level}.shp'
 gs=gpd.read_file(gsfile,bbox=(lon-.03,lat-.03,lon+.03,lat+.03))
 candidates=[g for g in gs.geometry if g.is_valid and g.covers(ref)]
 if len(candidates)!=1:raise RuntimeError(f'{c["name"]}: expected one GSHHG island, got {len(candidates)}')
 baseline=candidates[0];chosen=baseline;source='https://www.soest.hawaii.edu/wessel/gshhg/';source_type=f'GSHHG 2.3.7 full-resolution L{level}'
 waters=[];osm_candidates=[]
 for element in (data or {}).get('elements',[]):
  tags=element.get('tags',{});g=geometry(element)
  if g is None or g.is_empty or not g.is_valid:continue
  if tags.get('place')=='island':
   parts=list(g.geoms) if g.geom_type=='MultiPolygon' else [g]
   for part in parts:
    # The reference is authoritative; lake holes may exclude a point but not its exterior.
    if Polygon(part.exterior).covers(ref) and .20<area(part)/area(baseline)<1.8:
     overlap=area(part.intersection(baseline))/max(area(baseline),1e-9)
     if overlap>.18:osm_candidates.append((len(part.exterior.coords),part,element))
  if tags.get('natural')=='water':waters.append((g,element))
 if osm_candidates:
  _,chosen,element=max(osm_candidates,key=lambda item:item[0])
  source=f'https://www.openstreetmap.org/{element["type"]}/{element["id"]}'
  source_type='OpenStreetMap physical place=island outline'
 if not .4*c['expected_area_km2']<area(chosen)<1.8*c['expected_area_km2']:raise RuntimeError('Unexpected island area: '+c['name'])
 inland=[];water_sources=[]
 for water,element in waters:
  # Exclude surrounding marine polygons and neighboring islands' water features.
  if chosen.covers(water.representative_point()) and water.area<chosen.area*.2:
   clipped=water.intersection(chosen)
   if not clipped.is_empty and clipped.geom_type in ('Polygon','MultiPolygon'):
    inland.append(clipped);water_sources.append(f'https://www.openstreetmap.org/{element["type"]}/{element["id"]}')
 lakelevel=4 if level==3 else 2
 bounds=chosen.bounds
 for water in ([] if inland else gpd.read_file(a.source_dir/'GSHHS_shp/f'/f'GSHHS_f_L{lakelevel}.shp',bbox=bounds).geometry):
  if water.is_valid and chosen.covers(water.representative_point()) and water.area<chosen.area*.2:inland.append(water.intersection(chosen))
 extra=out/(c['id']+'-'+c['slug']+'-additional-water.geojson')
 if extra.exists():
  feature=json.loads(extra.read_text());extra_water=shape(feature['geometry'])
  if not chosen.covers(extra_water.representative_point()):raise RuntimeError('Supplementary lake lies outside island')
  inland.append(extra_water.intersection(chosen));water_sources.append(feature['properties']['source'])
 water=unary_union(inland)
 prefix=c['id']+'-'+c['slug']
 (out/(prefix+'-coastline.geojson')).write_text(json.dumps(mapping(chosen)))
 (out/(prefix+'-water.geojson')).write_text(json.dumps(mapping(water)))
 meta={**c,'coastline_source':source,'coastline_feature_type':source_type,'coastline_points':len(chosen.exterior.coords),'area_km2':area(chosen),'gshhg_area_km2':area(baseline),'gshhg_overlap_fraction':area(chosen.intersection(baseline))/area(baseline),'water_sources':water_sources,'water_count':len(list(water.geoms)) if hasattr(water,'geoms') else 0 if water.is_empty else 1,'reference_checked':True,'political_boundaries':False}
 (out/(prefix+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 results.append(meta);print(c['id'],c['name'],round(area(chosen),2),'km²',source_type,meta['water_count'],'water features',flush=True)
(out/'geography-validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')

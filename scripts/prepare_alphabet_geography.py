"""Prepare A–Z physical shorelines, mapped lakes and Gazetteer settlement evidence.

Requires an extracted GSHHG 2.3.7 full-resolution shapefile archive and the
GeoNames cities500 dump. These are physical outlines, never country polygons.
"""
import argparse,csv,io,json,zipfile
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point,mapping,Polygon
from shapely.ops import unary_union
from pyproj import Geod

p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);p.add_argument('--cities',type=Path,required=True);a=p.parse_args()
out=Path('data/collections/alphabet-000101-000126')
configs=json.loads((out/'collection-config.json').read_text())
geod=Geod(ellps='WGS84')
area=lambda g:abs(geod.geometry_area_perimeter(g)[0])/1e6
cities=[]
with zipfile.ZipFile(a.cities) as archive:
 with archive.open('cities500.txt') as data:
  for row in csv.reader(io.TextIOWrapper(data,encoding='utf8'),delimiter='\t'):
   cities.append(dict(name=row[1],country=row[8],lon=float(row[5]),lat=float(row[4]),population=int(row[14] or 0),source='https://www.geonames.org/'+row[0]))
results=[]
for c in configs:
 lon,lat=c['reference'];ref=Point(lon,lat)
 frame=gpd.read_file(a.source_dir/'GSHHS_shp/f/GSHHS_f_L1.shp',bbox=(lon-.015,lat-.015,lon+.015,lat+.015))
 candidates=[g for g in frame.geometry if g.is_valid and g.covers(ref)]
 if len(candidates)!=1:raise RuntimeError(c['name']+': expected exactly one physical island at reference, found '+str(len(candidates)))
 chosen=candidates[0]
 if chosen.area>30:raise RuntimeError('Unexpected continent-sized outline: '+c['name'])
 waters=[]
 for g in gpd.read_file(a.source_dir/'GSHHS_shp/f/GSHHS_f_L2.shp',bbox=chosen.bounds).geometry:
  if g.is_valid and chosen.covers(g.representative_point()):waters.append(g.intersection(chosen))
 water=unary_union(waters)
 settlements=[s for s in cities if s['country']==c['country_code'] and chosen.covers(Point(s['lon'],s['lat']))]
 settlement=max(settlements,key=lambda s:s['population']) if settlements else None
 if settlement:c['largest_settlement']=settlement['name']
 meta={**c,'coastline_source':'https://www.soest.hawaii.edu/wessel/gshhg/','coastline_feature_type':'GSHHG 2.3.7 full-resolution L1','coastline_points':len(chosen.exterior.coords),'area_km2':area(chosen),'gshhg_area_km2':area(chosen),'gshhg_overlap_fraction':1.0,'water_sources':['GSHHG 2.3.7 full-resolution L2'] if waters else [],'water_count':len(waters),'reference_checked':True,'political_boundaries':False,'largest_settlement_evidence':settlement,'settlement_note':'Highest population among GeoNames cities500 points inside the physical shoreline; not independently exhaustive.'}
 prefix=c['id']+'-'+c['slug']
 for suffix,g in [('coastline',chosen),('water',water)]:
  (out/(prefix+'-'+suffix+'.geojson')).write_text(json.dumps(mapping(g),separators=(',',':'))+'\n')
 (out/(prefix+'.json')).write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n')
 results.append(meta);print(c['id'],c['name'],round(meta['area_km2'],2),'km²;',len(waters),'mapped lakes;',c['largest_settlement'],flush=True)
(out/'geography-validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')

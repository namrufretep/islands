"""Render the African collection from physical coastlines and public elevation.

Requires NumPy, SciPy, Pillow, Shapely, PyProj, Rasterio and GeoPandas.
No political polygons, invented terrain, text or labels enter the artwork.
"""
import argparse,json,math,hashlib,urllib.request,urllib.error,time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from scipy.ndimage import gaussian_filter,distance_transform_edt
from PIL import Image,ImageFilter,ImageChops
import rasterio
from rasterio.merge import merge
from rasterio.warp import reproject,Resampling,transform_bounds
from rasterio.transform import from_bounds
from rasterio.features import rasterize
from shapely.geometry import shape,mapping
from shapely.ops import transform as shape_transform
from pyproj import Transformer

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--id');p.add_argument('--resume',action='store_true');p.add_argument('--source',type=Path,default=Path('public/drafts/africa-sources-20261126'));p.add_argument('--edition-dir',default='africa-20261126');a=p.parse_args()
source=a.source
configs=json.loads((source/'geography-validation.json').read_text())
a.cache.mkdir(parents=True,exist_ok=True)
def hexrgb(text):return np.array([int(text[i:i+2],16) for i in (1,3,5)],dtype=np.float32)
def fetch_tile(item):
 zoom,x,y=item;target=a.cache/f'{zoom}-{x}-{y}.tif'
 url=f'https://s3.amazonaws.com/elevation-tiles-prod/geotiff/{zoom}/{x}/{y}.tif'
 if not target.exists():
  for attempt in range(3):
   try:
    with urllib.request.urlopen(url,timeout=60) as response:data=response.read(15_000_001)
    break
   except urllib.error.HTTPError as error:
    if error.code not in (500,502,503,504) or attempt==2:raise
    time.sleep(2*(attempt+1))
  if len(data)>15_000_000:raise ValueError('Elevation tile too large')
  target.write_bytes(data)
 return target,url
def tile(lon,lat,z):return int((lon+180)/360*2**z),int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*2**z)
validations=[]
for c in configs:
 if a.id and c['id']!=a.id:continue
 prefix=c['id']+'-'+c['slug']
 existing_dir=Path('public/drafts')/c['id']/a.edition_dir
 existing=[]
 if a.resume:
  for e in ['N','S']:
   meta_file=existing_dir/(c['id']+'-'+e+'-draft.json');png_file=meta_file.with_suffix('.png')
   if meta_file.exists() and png_file.exists():
    meta=json.loads(meta_file.read_text())
    if meta.get('source')==c['coastline_source'] and meta.get('water_count')==c['water_count'] and meta.get('background')==c['palettes'][e][1] and meta['artwork_sha256']==hashlib.sha256(png_file.read_bytes()).hexdigest():existing.append(meta)
  if len(existing)==2:
   validations.append({k:existing[0][k] for k in ['id','name','land_coverage_fraction','min_land_elevation_m','max_land_elevation_m','terrain_tiles','resolution_m']})
   print(c['id'],c['name'],'verified existing pair',flush=True);continue
 geographic=shape(json.loads((source/(prefix+'-coastline.geojson')).read_text()))
 water=shape(json.loads((source/(prefix+'-water.geojson')).read_text()))
 lon,lat=c['reference'];crs=f'+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84 +units=m +no_defs'
 project=Transformer.from_crs('EPSG:4326',crs,always_xy=True).transform
 coast=shape_transform(project,geographic);water=shape_transform(project,water)
 x0,y0,x1,y1=coast.bounds;cx=(x0+x1)/2;cy=(y0+y1)/2;extent=max(x1-x0,y1-y0);full=extent/.85
 bounds=(cx-full/2,cy-full/2,cx+full/2,cy+full/2)
 resolution=full/512;transform=from_bounds(*bounds,512,512)
 zoom=12 if extent<12000 else 11
 west,south,east,north=transform_bounds(crs,'EPSG:4326',*bounds,densify_pts=21)
 tx0,ty0=tile(west,north,zoom);tx1,ty1=tile(east,south,zoom)
 items=[(zoom,x,y) for x in range(tx0,tx1+1) for y in range(ty0,ty1+1)]
 while len(items)>20 and zoom>5:
  zoom-=1;tx0,ty0=tile(west,north,zoom);tx1,ty1=tile(east,south,zoom)
  items=[(zoom,x,y) for x in range(tx0,tx1+1) for y in range(ty0,ty1+1)]
 if len(items)>20:raise RuntimeError('Unexpected terrain extent')
 with ThreadPoolExecutor(max_workers=3) as pool:tiles=list(pool.map(fetch_tile,items))
 datasets=[rasterio.open(path) for path,_ in tiles]
 mosaic,src_transform=merge(datasets)
 terrain=np.full((512,512),np.nan,dtype=np.float32)
 reproject(mosaic[0],terrain,src_transform=src_transform,src_crs=datasets[0].crs,src_nodata=datasets[0].nodata,dst_transform=transform,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear)
 for ds in datasets:ds.close()
 land=rasterize([(coast,1)],out_shape=(512,512),transform=transform,dtype='uint8').astype(bool)
 valid=np.isfinite(terrain);coverage=float(valid[land].mean())
 if coverage<.995:raise RuntimeError(f'{c["name"]}: incomplete land terrain coverage {coverage}')
 terrain=terrain[tuple(distance_transform_edt(~valid,return_distances=False,return_indices=True))]
 broad=gaussian_filter(terrain,13);low,high=np.percentile(broad[land],[3,99]);elevation=np.clip((broad-low)/max(high-low,1),0,1)
 inward=distance_transform_edt(land)*4
 rounded=1-np.exp(-inward/105)
 body=gaussian_filter(rounded*(.38+.62*elevation),6.5)
 dy,dx=np.gradient(body,4);dx*=220;dy*=220
 # Rasterize the exact physical silhouette independently at final resolution.
 alpha=Image.fromarray(rasterize([(coast,255)],out_shape=(2048,2048),transform=from_bounds(*bounds,2048,2048),dtype='uint8'))
 water_mask=Image.fromarray(rasterize([(water,255)],out_shape=(2048,2048),transform=from_bounds(*bounds,2048,2048),dtype='uint8')) if not water.is_empty else None
 out=Path('public/drafts')/c['id']/a.edition_dir;out.mkdir(parents=True,exist_ok=True)
 validation=dict(id=c['id'],name=c['name'],land_coverage_fraction=coverage,min_land_elevation_m=float(terrain[land].min()),max_land_elevation_m=float(terrain[land].max()),terrain_tiles=[url for _,url in tiles],resolution_m=resolution)
 validations.append(validation)
 for edition,angle,sign in [('N',0,1),('S',180,-1)]:
  palette,background,mood=c['palettes'][edition]
  hill=(math.sin(math.pi/4)+sign*math.cos(math.pi/4)*(dx+dy)/math.sqrt(2))/np.sqrt(1+dx*dx+dy*dy)
  lighting=gaussian_filter(.68*hill+.32*elevation,4)
  lo,hi=np.percentile(lighting[land],[3,97]);tone=np.clip((lighting-lo)/max(hi-lo,.025),0,1)
  tone=.10+.80*(.55*tone*tone*(3-2*tone)+.45*tone);tone=gaussian_filter(tone,.8)
  colors=np.array([hexrgb(color) for color in palette]);position=tone*3;index=np.minimum(position.astype(int),2);fraction=(position-index)[...,None]
  rgb=colors[index]*(1-fraction)+colors[index+1]*fraction
  art=Image.fromarray(np.clip(rgb,0,255).astype('uint8')).resize((2048,2048),Image.Resampling.LANCZOS)
  current_alpha=alpha;current_water=water_mask
  if angle:
   art=art.rotate(angle);current_alpha=alpha.rotate(angle);current_water=water_mask.rotate(angle) if water_mask else None
  # A restrained broad wash and close, soft shadow; no height steps or outlines.
  yy,xx=np.mgrid[0:512,0:512];wash=(.5-(.6*xx+.4*yy)/511)[...,None]*.09
  base=hexrgb(background)[None,None,:]
  background_rgb=np.clip(base+(255-base)*np.maximum(wash,0)+base*np.minimum(wash,0),0,255).astype('uint8')
  canvas=Image.fromarray(background_rgb).resize((2048,2048),Image.Resampling.BILINEAR).convert('RGBA')
  blurred=current_alpha.filter(ImageFilter.GaussianBlur(15)).point(lambda x:round(x*.20))
  shadow=Image.new('RGBA',(2048,2048),tuple(np.maximum(hexrgb(background)*.36,8).astype('uint8'))+(0,));shadow.putalpha(blurred)
  canvas.alpha_composite(shadow,dest=(11,19))
  art=art.convert('RGBA');art.putalpha(current_alpha);canvas.alpha_composite(art)
  if current_water:
   surface=Image.new('RGBA',(2048,2048),tuple(np.clip(hexrgb(background)*.96,0,255).astype('uint8'))+(255,));surface.putalpha(current_water);canvas.alpha_composite(surface)
  stem=out/(c['id']+'-'+edition+'-draft');png=stem.with_suffix('.png');canvas.convert('RGB').save(png,dpi=(300,300),optimize=True)
  metadata={**c,**validation,'id':c['id'],'edition':edition,'orientation_degrees':angle,'status':'verified_coastline','source':c['coastline_source'],'projection':crs,'bounds_m':[x0,y0,x1,y1],'canvas_px':2048,'dpi_target':300,'artwork_extent_px':1740.8,'artwork_meters_per_pixel':full/2048,'artwork_print_scale_denominator':full/2048*300/.0254,'color_mood':mood,'background':background,'background_name':c['background_names'][edition],'color_family':c['color_families'][edition],'palette':palette,'art_version':'4.5-alphabet' if a.edition_dir.startswith('alphabet') else '4.4-africa','art_status':'experimental_draft','terrain_guided':True,'whole_island_terrain':True,'surface_finish':'bouvet_wash','surface_model':'Soft Stone: continuous rounded mineral relief from physical shoreline and public elevation','lighting':{'screen_direction':'upper_left','elevation_degrees':45,'shared_surface':True},'political_boundaries':False,'attribution':('GSHHG 2.3.7 / Wessel and Smith, LGPL-3.0-or-later; GeoNames CC BY 4.0; Mapzen elevation tiles'+('; © OpenStreetMap contributors, ODbL' if any('openstreetmap.org' in url for url in c.get('water_sources',[])) else '')) if a.edition_dir.startswith('alphabet') else '© OpenStreetMap contributors, ODbL; GSHHG 2.3.7 / Wessel and Smith, LGPL-3.0-or-later; Mapzen elevation tiles','artwork_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'geography_note':'Physical shoreline cross-checked against GSHHG; areas are approximate polygon areas. Inland waters are mapped selections, not exhaustive. Relief is an artistic interpretation of elevation.'}
  stem.with_suffix('.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
  print(c['id'],c['name'],edition,'rendered',png.stat().st_size,'bytes',flush=True)
 del canvas,art,alpha,terrain,mosaic
(source/'terrain-validation.json').write_text(json.dumps(validations,ensure_ascii=False,indent=2)+'\n')

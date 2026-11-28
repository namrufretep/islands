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
from island_lighting import hillshade, directional_component, horizontal_unit, shadow_offset, validate_design
from chromatic_surface import chromatic_surface

p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True);p.add_argument('--id');p.add_argument('--resume',action='store_true');p.add_argument('--source',type=Path,default=Path('public/drafts/africa-sources-20261126'));p.add_argument('--edition-dir',default='africa-20261126');p.add_argument('--style',choices=['rounded','bouvet-original'],default='rounded');p.add_argument('--variable-lighting',action='store_true');a=p.parse_args()
if a.variable_lighting and a.style!='bouvet-original':p.error('Variable lighting requires the Bouvet surface')
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
 if a.variable_lighting:
  for e in ['N','S']:validate_design(c['lighting_design'][e])
 prefix=c['id']+'-'+c['slug']
 existing_dir=Path('public/drafts')/c['id']/a.edition_dir
 existing=[]
 if a.resume:
  for e in ['N','S']:
   meta_file=existing_dir/(c['id']+'-'+e+'-draft.json');png_file=meta_file.with_suffix('.png')
   if meta_file.exists() and png_file.exists():
    meta=json.loads(meta_file.read_text())
    lighting_matches=meta.get('variable_lighting',False)==a.variable_lighting
    if a.variable_lighting:
     design=c['lighting_design'][e]
     lighting_matches=lighting_matches and all(meta.get('lighting',{}).get(k)==design[k] for k in ['azimuth_degrees','elevation_degrees']) and meta.get('lighting',{}).get('shadow_offset_px')==list(shadow_offset(design['azimuth_degrees'],design['shadow_distance_px']))
    colour_matches=meta.get('palette')==c['palettes'][e][0] and meta.get('chromatic_design')==c.get('chromatic_design',{}).get(e)
    if c.get('chromatic_design'):colour_matches=colour_matches and meta.get('chromatic_model_revision')==3
    if lighting_matches and colour_matches and meta.get('source')==c['coastline_source'] and meta.get('water_count')==c['water_count'] and meta.get('background')==c['palettes'][e][1] and meta.get('render_style','rounded')==a.style and meta['artwork_sha256']==hashlib.sha256(png_file.read_bytes()).hexdigest():existing.append(meta)
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
 crosses_antimeridian=west>east
 def tile_items(z):
  tx0,ty0=tile(west,north,z);tx1,ty1=tile(east,south,z)
  xs=list(range(tx0,2**z))+list(range(0,tx1+1)) if crosses_antimeridian else range(tx0,tx1+1)
  return [(z,x,y) for x in xs for y in range(ty0,ty1+1)]
 items=tile_items(zoom)
 while len(items)>20 and zoom>5:
  zoom-=1;items=tile_items(zoom)
 if len(items)>20:raise RuntimeError('Unexpected terrain extent')
 with ThreadPoolExecutor(max_workers=3) as pool:tiles=list(pool.map(fetch_tile,items))
 datasets=[rasterio.open(path) for path,_ in tiles]
 mosaic=None
 terrain=np.full((512,512),np.nan,dtype=np.float32)
 if crosses_antimeridian:
  # Reproject the two sides separately to avoid a world-wide Mercator mosaic.
  for ds in datasets:
   reproject(rasterio.band(ds,1),terrain,src_transform=ds.transform,src_crs=ds.crs,src_nodata=ds.nodata,dst_transform=transform,dst_crs=crs,dst_nodata=np.nan,resampling=Resampling.bilinear,init_dest_nodata=False)
 else:
  mosaic,src_transform=merge(datasets)
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
 if a.style=='bouvet-original':
  # Bouvet 3.8: a single broad sculpted light field, evaluated in normalized
  # artwork space so that island size does not change the visual softness.
  coast_distance=gaussian_filter(distance_transform_edt(land),2)
  distance=gaussian_filter(coast_distance,5)
  distance/=max(float(distance.max()),1)
  relief=gaussian_filter(gaussian_filter(terrain,8),13)
  low,high=np.percentile(relief[land],[3,99])
  relief=np.clip((relief-low)/max(float(high-low),1),0,1)
  body=gaussian_filter((1-np.exp(-distance*5))*land*(.25+.75*relief),7)
  # The original reference spans about 11.5 km including the canvas margins.
  height=1400*full/11521
  dy,dx=np.gradient(body*height,resolution)
  edge_y,edge_x=np.gradient(coast_distance,resolution)
 # Rasterize the exact physical silhouette independently at final resolution.
 alpha=Image.fromarray(rasterize([(coast,255)],out_shape=(2048,2048),transform=from_bounds(*bounds,2048,2048),dtype='uint8'))
 water_mask=Image.fromarray(rasterize([(water,255)],out_shape=(2048,2048),transform=from_bounds(*bounds,2048,2048),dtype='uint8')) if not water.is_empty else None
 out=Path('public/drafts')/c['id']/a.edition_dir;out.mkdir(parents=True,exist_ok=True)
 validation=dict(id=c['id'],name=c['name'],land_coverage_fraction=coverage,min_land_elevation_m=float(terrain[land].min()),max_land_elevation_m=float(terrain[land].max()),terrain_tiles=[url for _,url in tiles],resolution_m=resolution)
 validations.append(validation)
 for edition,angle,sign in [('N',0,1),('S',180,-1)]:
  palette,background,mood=c['palettes'][edition]
  hill=(math.sin(math.pi/4)+sign*math.cos(math.pi/4)*(dx+dy)/math.sqrt(2))/np.sqrt(1+dx*dx+dy*dy)
  if a.variable_lighting:
   design=c['lighting_design'][edition]
   hill=hillshade(dx,dy,design['azimuth_degrees'],design['elevation_degrees'],angle)
  if a.style=='bouvet-original':
   lighting=np.clip(.15+.85*gaussian_filter(hill,9),0,1)
   bevel=directional_component(edge_x,edge_y,design['azimuth_degrees'],angle) if a.variable_lighting else sign*(edge_x+edge_y)/math.sqrt(2)
   lighting+=.105*bevel*np.exp(-coast_distance/9)
   lo,hi=np.percentile(lighting[land],[3,97])
   if hi-lo<.025:raise RuntimeError('Insufficient broad relief contrast: '+c['name'])
   tone=np.clip((lighting-lo)/(hi-lo),0,1)
   tone=tone*tone*(3-2*tone)
  else:
   lighting=gaussian_filter(.68*hill+.32*elevation,4)
   lo,hi=np.percentile(lighting[land],[3,97]);tone=np.clip((lighting-lo)/max(hi-lo,.025),0,1)
   tone=.10+.80*(.55*tone*tone*(3-2*tone)+.45*tone);tone=gaussian_filter(tone,.8)
  if c.get('chromatic_design'):
   rgb,colour_field=chromatic_surface(relief,coast_distance,land,tone,palette,c['chromatic_design'][edition])
  else:
   colors=np.array([hexrgb(color) for color in palette]);position=tone*(len(colors)-1);index=np.minimum(position.astype(int),len(colors)-2);fraction=(position-index)[...,None]
   rgb=colors[index]*(1-fraction)+colors[index+1]*fraction
  art=Image.fromarray(np.clip(rgb,0,255).astype('uint8')).resize((2048,2048),Image.Resampling.LANCZOS)
  current_alpha=alpha;current_water=water_mask
  if angle:
   art=art.rotate(angle);current_alpha=alpha.rotate(angle);current_water=water_mask.rotate(angle) if water_mask else None
  # A restrained broad wash and close, soft shadow; no height steps or outlines.
  yy,xx=np.mgrid[0:512,0:512];wash=(.5-(.6*xx+.4*yy)/511)[...,None]*.09
  if a.variable_lighting:
   lx,ly=horizontal_unit(design['azimuth_degrees'])
   wash=(((xx-255.5)*lx+(yy-255.5)*ly)/(511*math.sqrt(2)))[...,None]*.09
  base=hexrgb(background)[None,None,:]
  background_rgb=np.clip(base+(255-base)*np.maximum(wash,0)+base*np.minimum(wash,0),0,255).astype('uint8')
  canvas=Image.fromarray(background_rgb).resize((2048,2048),Image.Resampling.BILINEAR).convert('RGBA')
  shadow_opacity=.08 if a.style=='bouvet-original' else .20
  blurred=current_alpha.filter(ImageFilter.GaussianBlur(15)).point(lambda x:round(x*shadow_opacity))
  shadow=Image.new('RGBA',(2048,2048),tuple(np.maximum(hexrgb(background)*.36,8).astype('uint8'))+(0,));shadow.putalpha(blurred)
  offset=shadow_offset(design['azimuth_degrees'],design['shadow_distance_px']) if a.variable_lighting else (4,7) if a.style=='bouvet-original' else (11,19)
  canvas.alpha_composite(shadow,dest=offset)
  art=art.convert('RGBA');art.putalpha(current_alpha);canvas.alpha_composite(art)
  if current_water:
   surface=Image.new('RGBA',(2048,2048),tuple(np.clip(hexrgb(background)*.96,0,255).astype('uint8'))+(255,));surface.putalpha(current_water);canvas.alpha_composite(surface)
  stem=out/(c['id']+'-'+edition+'-draft');png=stem.with_suffix('.png');canvas.convert('RGB').save(png,dpi=(300,300),optimize=True)
  metadata={**c,**validation,'id':c['id'],'edition':edition,'orientation_degrees':angle,'status':'verified_coastline','source':c['coastline_source'],'projection':crs,'bounds_m':[x0,y0,x1,y1],'canvas_px':2048,'dpi_target':300,'artwork_extent_px':1740.8,'artwork_meters_per_pixel':full/2048,'artwork_print_scale_denominator':full/2048*300/.0254,'color_mood':mood,'background':background,'background_name':c['background_names'][edition],'color_family':c['color_families'][edition],'palette':palette,'art_version':'4.5-alphabet' if a.edition_dir.startswith('alphabet') else '4.4-africa','art_status':'experimental_draft','terrain_guided':True,'whole_island_terrain':True,'surface_finish':'bouvet_wash','surface_model':'Soft Stone: continuous rounded mineral relief from physical shoreline and public elevation','lighting':{'screen_direction':'upper_left','elevation_degrees':45,'shared_surface':True},'political_boundaries':False,'attribution':('GSHHG 2.3.7 / Wessel and Smith, LGPL-3.0-or-later; GeoNames CC BY 4.0; Mapzen elevation tiles'+('; © OpenStreetMap contributors, ODbL' if any('openstreetmap.org' in url for url in c.get('water_sources',[])) else '')) if a.edition_dir.startswith('alphabet') else '© OpenStreetMap contributors, ODbL; GSHHG 2.3.7 / Wessel and Smith, LGPL-3.0-or-later; Mapzen elevation tiles','artwork_sha256':hashlib.sha256(png.read_bytes()).hexdigest(),'geography_note':'Physical shoreline cross-checked against GSHHG; areas are approximate polygon areas. Inland waters are mapped selections, not exhaustive. Relief is an artistic interpretation of elevation.'}
  metadata['render_style']=a.style
  if a.style=='bouvet-original':
   metadata.update(art_version='4.6-bouvet',surface_finish='bouvet_original',surface_model='Soft Stone: broad continuous DEM-guided light fields and a normalized sculpted dome',style_reference={'island_id':'000001','art_version':'3.8','reference':'Bouvetøya original North-Up and South-Up'},shadow_opacity=shadow_opacity)
   metadata['attribution']='GSHHG 2.3.7 / Wessel and Smith, LGPL-3.0-or-later; GeoNames CC BY 4.0; Mapzen elevation tiles'
  if a.variable_lighting:
   metadata.update(art_version='4.7-bouvet-directional',variable_lighting=True)
   metadata['lighting']={**design,'shared_surface':True,'azimuth_convention':'clockwise from screen top','horizontal_light_vector':[lx,ly],'shadow_offset_px':list(offset),'consistent_relief_and_cast_shadow':True}
  if c.get('chromatic_design'):
   metadata.update(art_version='4.8-bouvet-chromatic',chromatic_model_revision=3,chromatic_design=c['chromatic_design'][edition],palette_stop_count=len(palette),colour_model='Continuous spatial/terrain colour field; directional sculptural light applied independently',chromatic_artistic_field=True)
  stem.with_suffix('.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
  print(c['id'],c['name'],edition,'rendered',png.stat().st_size,'bytes',flush=True)
 del canvas,art,alpha,terrain,mosaic
(source/'terrain-validation.json').write_text(json.dumps(validations,ensure_ascii=False,indent=2)+'\n')

"""Export exact A–Z originals with their metadata and a labelled review sheet."""
import argparse,json,zipfile,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--source',type=Path,default=Path('data/collections/alphabet-000101-000126'));p.add_argument('--edition-dir',default='alphabet-20261127');p.add_argument('--name',default='Islands_000101-000126_A-Z');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
source=a.source;configs=json.loads((source/'geography-validation.json').read_text())
w=256;h=288;overview=Image.new('RGB',(8*w,((len(configs)*2+7)//8)*h),'#e6dfd0');draw=ImageDraw.Draw(overview)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
files=[]
for i,c in enumerate(configs):
 for j,e in enumerate(['N','S']):
  path=Path('public/drafts')/c['id']/a.edition_dir/f'{c["id"]}-{e}-draft.png'
  meta=json.loads(path.with_suffix('.json').read_text());assert hashlib.sha256(path.read_bytes()).hexdigest()==meta['artwork_sha256']
  image=Image.open(path);assert image.size==(2048,2048);image.thumbnail((w,w),Image.Resampling.LANCZOS)
  x=(i*2+j)%8*w;y=(i*2+j)//8*h;overview.paste(image,(x,y));label=f'{c["letter"]} · {c["name"]} · {e}'
  while draw.textlength(label,font=font)>w-12:label=label[:-2]+'…'
  draw.text((x+6,y+260),label,font=font,fill='#103321');files.extend([path,path.with_suffix('.json')])
sheet=a.output/(a.name+'_Overview.png');overview.save(sheet,dpi=(300,300))
with zipfile.ZipFile(a.output/(a.name+'.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,'artworks/'+f.name)
 for f in sorted(source.iterdir()):
  if f.is_file():z.write(f,'sources/'+f.name)
 for name in ['prepare_alphabet_geography.py','render_african_collection.py','island_lighting.py','test_island_lighting.py','chromatic_surface.py','test_chromatic_surface.py','alphabet_water.py','register_alphabet_collection.py','export_alphabet_collection.py']:z.write('scripts/'+name,'scripts/'+name)
 z.write(sheet,sheet.name)
print('Exported',len(configs)*2,'original artworks, metadata, source geometries, scripts and overview')

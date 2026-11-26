"""Create the review contact sheet and complete portable artwork package."""
import json,shutil,zipfile,hashlib,argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
configs=json.loads(Path('data/collections/africa-000064-000075.json').read_text())
a.output.mkdir(parents=True,exist_ok=True)
package=a.output/'Islands_000064-000075';package.mkdir(exist_ok=True)
width,height=320,355
overview=Image.new('RGB',(width*4,height*6),(237,234,225));draw=ImageDraw.Draw(overview)
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',16)
for i,c in enumerate(configs):
 for j,(edition,orientation) in enumerate([('N','North'),('S','South')]):
  original=Path('public/drafts')/c['id']/'africa-20261126'/(c['id']+'-'+edition+'-draft.png')
  metadata=json.loads(original.with_suffix('.json').read_text())
  assert hashlib.sha256(original.read_bytes()).hexdigest()==metadata['artwork_sha256']
  stem=package/('Islands_'+c['id']+'_'+orientation+'_Up')
  shutil.copy2(original,stem.with_suffix('.png'));shutil.copy2(original.with_suffix('.json'),stem.with_suffix('.json'))
  n=i*2+j;x=n%4*width;y=n//4*height
  image=Image.open(original);image.thumbnail((320,320),Image.Resampling.LANCZOS)
  overview.paste(image,(x,y));draw.text((x+8,y+325),c['id']+' '+c['name']+' · '+edition,font=font,fill=(30,48,44))
overview_path=a.output/'Islands_000064-000075_Overview.png';overview.save(overview_path,dpi=(300,300))
shutil.copy2(overview_path,package/overview_path.name)
sources=Path('public/drafts/africa-sources-20261126');shutil.copytree(sources,package/'sources',dirs_exist_ok=True)
shutil.copy2(sources/'README.txt',package/'README.txt')
for file in ['prepare_african_geography.py','render_african_collection.py','register_african_collection.py','export_african_collection.py']:
 (package/'scripts').mkdir(exist_ok=True);shutil.copy2(Path('scripts')/file,package/'scripts'/file)
shutil.copy2('data/collections/africa-000064-000075.json',package/'sources/collection-config.json')
zip_path=a.output/'Islands_000064-000075.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as archive:
 for file in sorted(package.rglob('*')):
  if file.is_file():archive.write(file,file.relative_to(package))
print('Exported 24 originals, overview, metadata, source geometry and scripts to',zip_path)

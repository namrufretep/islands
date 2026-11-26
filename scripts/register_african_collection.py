"""Register the completed 000064–000075 artwork without duplicate entries."""
from pathlib import Path
import json,re,hashlib

p=Path('src/main.js');source=p.read_text()
keys=['previewEditions','registry','draftIds','draftTraits','islandFacts','curatedGeoNamesIds']
values={key:json.loads(re.search('const '+key+'=(.*?);',source).group(1)) for key in keys}
configs=json.loads(Path('data/collections/africa-000064-000075.json').read_text())
for c in configs:
 island_id=c['id'];name=c['name'];lon,lat=c['reference']
 for edition,orientation in [('N','North-Up'),('S','South-Up')]:
  image=f'/drafts/{island_id}/africa-20261126/{island_id}-{edition}-draft.png'
  metadata=json.loads(Path('public'+image.replace('.png','.json')).read_text())
  assert hashlib.sha256(Path('public'+image).read_bytes()).hexdigest()==metadata['artwork_sha256']
  entry=dict(id=island_id+'-'+edition,islandId=island_id,name=name,orientation=orientation,mood=metadata['color_mood'],image=image,status='Preview',collection='African Islands')
  values['previewEditions']=[e for e in values['previewEditions'] if e['id']!=entry['id']]+[entry]
  if edition=='N':values['islandFacts'][name]=dict(area=round(metadata['area_km2'],1),sovereignty=c['country'])
 values['registry']=[r for r in values['registry'] if r[0]!=name]+[[name,c['country'],c['region'],lat,lon]]
 values['draftIds'][name]=island_id
 values['draftTraits'][name]=[c['region'],c['island_type'],c['water_type'],c['ocean'],c['water_body'],c['color_families']['N'],c['color_families']['S'],c['background_names']['N'],c['background_names']['S'],None]
 if c['source_id'] not in values['curatedGeoNamesIds']:values['curatedGeoNamesIds'].append(c['source_id'])
for key,value in values.items():source=re.sub('const '+key+'=.*?;',lambda m:'const '+key+'='+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';',source,count=1)
p.write_text(source)
print('Registered',len(configs),'African island pairs;',len(values['previewEditions']),'total editions')

"""Register 26 completed A–Z island pairs without creating minted inventory."""
from pathlib import Path
import json,re,hashlib,argparse
a=argparse.ArgumentParser();a.add_argument('--source',type=Path,default=Path('data/collections/alphabet-000101-000126'));a.add_argument('--edition-dir',default='alphabet-20261127');args=a.parse_args()
p=Path('src/main.js');source=p.read_text()
keys=['previewEditions','registry','draftIds','draftTraits','islandFacts','curatedGeoNamesIds']
v={key:json.loads(re.search('const '+key+'=(.*?);',source).group(1)) for key in keys}
configs=json.loads((args.source/'geography-validation.json').read_text())
review_path=Path('public/data/island-index-review.json');review=json.loads(review_path.read_text())
for c in configs:
 island_id,name=c['id'],c['name'];lon,lat=c['reference']
 assert name[0].upper()==c['letter']
 for e,orientation in [('N','North-Up'),('S','South-Up')]:
  image=f'/drafts/{island_id}/{args.edition_dir}/{island_id}-{e}-draft.png';png=Path('public'+image);meta=json.loads(png.with_suffix('.json').read_text())
  assert meta['artwork_sha256']==hashlib.sha256(png.read_bytes()).hexdigest()
  entry=dict(id=island_id+'-'+e,islandId=island_id,name=name,orientation=orientation,mood=meta['color_mood'],image=image,status='Preview',collection=c.get('collection','A–Z Islands'))
  v['previewEditions']=[x for x in v['previewEditions'] if x['id']!=entry['id']]+[entry]
  if e=='N':v['islandFacts'][name]=dict(area=round(meta['area_km2'],2),sovereignty=c['country'])
 v['registry']=[r for r in v['registry'] if r[0]!=name]+[[name,c['country'],c['region'],lat,lon]]
 v['draftIds'][name]=island_id
 v['draftTraits'][name]=[c['region'],c['island_type'],c['water_type'],c['ocean'],c['water_body'],c['color_families']['N'],c['color_families']['S'],c['background_names']['N'],c['background_names']['S'],c['largest_settlement']]
 if c['source_id'] not in v['curatedGeoNamesIds']:v['curatedGeoNamesIds'].append(c['source_id'])
 review['curated'][name]=dict(areaKm2=c['area_km2'],areaSource='GSHHG 2.3.7 physical shoreline; geodesic polygon area; approximate')
 if c['source_id'] not in review['curatedAliases']:review['curatedAliases'].append(c['source_id'])
for key,value in v.items():source=re.sub('const '+key+'=.*?;',lambda m:'const '+key+'='+json.dumps(value,ensure_ascii=False,separators=(',',':'))+';',source,count=1)
source=source.replace('any of the 100 original islands','any original island')
p.write_text(source)
review_path.write_text(json.dumps(review,ensure_ascii=False,separators=(',',':'))+'\n')
report_path=Path('docs/index-data-review.json');report=json.loads(report_path.read_text());report['curated_registry_entries_checked']=len(v['registry']);report['curated_entries_with_areas']=sum('areaKm2' in x for x in review['curated'].values());report['curated_alias_ids']=len(review['curatedAliases']);report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Registered A–Z:',len(configs),'islands;',len(v['previewEditions']),'total preview editions; no original NFT minted')

"""Audit every GeoNames island and attach conservative GSHHG point matches.

No names are merged on spelling alone. Areas are approximate shoreline-database
areas, not surveyed land areas. Mainland, ambiguous and unmatched points stay
unresolved. Original registry records and source IDs remain intact.
"""
import argparse,collections,json,math,re,unicodedata
from pathlib import Path
import geopandas as gpd
import numpy as np
import shapely

p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True);args=p.parse_args()
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'public/data/world-islands.json').read_text())
source=(root/'src/main.js').read_text()
registry=json.loads(re.search(r'const registry=(.*?);',source)[1])
ids=json.loads(re.search(r'const draftIds=(.*?);',source)[1])
editions=json.loads(re.search(r'const previewEditions=(.*?);',source)[1])
def norm(s):return ''.join(c for c in unicodedata.normalize('NFKD',s.casefold()) if c.isalnum())
def distance(a,b):
 p,q=map(math.radians,[a['latitude'],b['latitude']]);d=math.radians(b['longitude']-a['longitude'])
 h=math.sin((p-q)/2)**2+math.cos(p)*math.cos(q)*math.sin(d/2)**2
 return 12742*math.asin(min(1,math.sqrt(h)))

geometries=[];features=[]
for level in (1,3):
 frame=gpd.read_file(args.source_dir/'GSHHS_shp/f'/f'GSHHS_f_L{level}.shp')
 for row in frame.itertuples():
  feature_id=str(row.id).split('-')[0]
  if level==1 and int(feature_id)<=6:continue # GSHHG's six continental polygons
  if not row.geometry.is_valid or row.geometry.is_empty or not row.area>0:continue
  geometries.append(row.geometry);features.append({'id':f'{level}:{feature_id}','level':level,'area':float(row.area)})
 print('Loaded shoreline level',level,flush=True)
tree=shapely.STRtree(geometries)
all_points=rows+[{'latitude':r[3],'longitude':r[4]} for r in registry]
points=shapely.points(np.array([r['longitude'] for r in all_points]),np.array([r['latitude'] for r in all_points]))
pairs=tree.query(points,predicate='within')
matches=collections.defaultdict(list)
for point_index,feature_index in zip(*pairs):matches[int(point_index)].append(features[int(feature_index)])
resolved={}
for i,options in matches.items():
 level=max(x['level'] for x in options);options={x['id']:x for x in options if x['level']==level}
 if len(options)==1:resolved[i]=next(iter(options.values()))
print('Matched points',len(resolved),flush=True)

names_by_feature=collections.defaultdict(set)
same_feature_name=collections.defaultdict(list)
same_name=collections.defaultdict(list)
for i,row in enumerate(rows):
 same_name[norm(row['name'])].append(i)
 if i in resolved:
  f=resolved[i];names_by_feature[f['id']].add(norm(row['name']))
  same_feature_name[(f['id'],norm(row['name']),row['countryCode'])].append(i)

duplicates={};duplicate_groups=[]
for key,indices in same_feature_name.items():
 if len(indices)<2:continue
 # Close, same-name/same-country records on the same physical polygon only.
 remaining=set(indices)
 while remaining:
  first=min(remaining,key=lambda i:int(rows[i]['sourceId'].split(':')[1]));remaining.remove(first)
  group=[first]+[i for i in remaining if distance(rows[first],rows[i])<=.2]
  for i in group[1:]:remaining.remove(i);duplicates[rows[i]['sourceId']]=rows[first]['sourceId']
  if len(group)>1:duplicate_groups.append({'canonical':rows[first]['sourceId'],'shorelineId':key[0],'members':[rows[i]['sourceId'] for i in group]})

curated={};curated_aliases=set()
for j,row in enumerate(registry):
 name=row[0];f=resolved.get(len(rows)+j);facts={}
 if f:facts.update(shorelineId=f['id'],shorelineAreaKm2=round(f['area'],6))
 edition=next((e for e in editions if e['name']==name and e['id'].endswith('-N')),None)
 if edition:
  metadata=json.loads((root/('public'+edition['image'].replace('.png','.json'))).read_text())
  if metadata.get('area_km2') is not None:facts.update(areaKm2=metadata['area_km2'],areaSource=metadata.get('attribution') or metadata.get('source') or 'Reviewed artwork geometry')
 elif f:facts.update(areaKm2=round(f['area'],6),areaSource='GSHHG 2.3.7; geographic point match; approximate')
 curated[name]=facts
 if f:
  for i in same_name[norm(name)]:
   if i in resolved and resolved[i]['id']==f['id']:curated_aliases.add(rows[i]['sourceId'])

shards=[{} for _ in range(32)];areas=0;ambiguous=0
for i,row in enumerate(rows):
 f=resolved.get(i)
 if not f:continue
 # Multiple differently named gazetteer islands in one polygon may be
 # subfeatures or imprecise points; do not assign each the whole polygon area.
 if len(names_by_feature[f['id']])!=1:ambiguous+=1;continue
 if row['sourceId'] in duplicates:continue
 source_id=int(row['sourceId'].split(':')[1]);shards[source_id%32][str(source_id)]={'areaKm2':round(f['area'],6),'shorelineId':f['id'],'waterType':'Freshwater' if f['level']==3 else 'Marine / coastal'};areas+=1
out=root/'public/data/island-details';out.mkdir(exist_ok=True)
for i,records in enumerate(shards):(out/f'{i}.json').write_text(json.dumps({'source':'GSHHG 2.3.7','records':records},ensure_ascii=False,separators=(',',':'))+'\n')
review={'version':1,'sourceRecords':len(rows),'duplicateOf':duplicates,'curatedAliases':sorted(curated_aliases),'curated':curated,'areaSource':'GSHHG 2.3.7; point-in-polygon match; approximate; not a survey','areaSourceUrl':'https://www.soest.hawaii.edu/wessel/gshhg/'}
(root/'public/data/island-index-review.json').write_text(json.dumps(review,ensure_ascii=False,separators=(',',':'))+'\n')
source_counts=collections.Counter(r['sourceId'] for r in rows)
report={'source_records_checked':len(rows),'duplicate_source_ids':[s for s,n in source_counts.items() if n>1],'confirmed_duplicate_groups':duplicate_groups,'suppressed_close_same_polygon_records':len(duplicates),'same_name_groups_retained_for_disambiguation':sum(len(v)>1 for v in same_name.values()),'missing_country_codes':sum(not r['countryCode'] for r in rows),'unique_shoreline_point_matches':sum(i<len(rows) for i in resolved),'approximate_areas_published':areas,'area_withheld_ambiguous_named_subfeatures':ambiguous,'area_unresolved_no_unique_match':len(rows)-sum(i<len(rows) for i in resolved),'curated_registry_entries_checked':len(registry),'curated_entries_with_areas':sum('areaKm2' in f for f in curated.values()),'curated_alias_ids':len(curated_aliases),'area_method':review['areaSource'],'limitations':['Gazetteer points and 2017 shorelines can be imprecise or outdated.','No area is inferred for mainland matches, unmatched points or competing names in one shoreline polygon.','Country gaps and settlements are not invented. Same names at different locations remain separate.','All original GeoNames records and IDs are retained in the source registry.']}
(root/'docs/index-data-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='confirmed_duplicate_groups'},ensure_ascii=False,indent=2),flush=True)

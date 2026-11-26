import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import vm from 'node:vm';
const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const value=name=>vm.runInNewContext('('+source.match(new RegExp('const '+name+'=(.*?);'))[1]+')');
const editions=value('previewEditions'),ids=value('draftIds'),traits=value('draftTraits'),registry=value('registry');
test('every existing island opens both distinct artwork editions and matching metadata',()=>{
 assert.equal(new Set(editions.map(e=>e.id)).size,editions.length);
 for(const [name,id] of Object.entries(ids)){
  assert.equal(registry.filter(r=>r[0]===name).length,1,name);
  assert.ok(traits[name],name+' traits');
  for(const e of ['N','S']){
   const edition=editions.find(x=>x.id===id+'-'+e);assert.ok(edition,name+' '+e);
   const image=new URL('../public'+edition.image,import.meta.url);
   assert.ok(existsSync(image),edition.image);
   const metadata=JSON.parse(readFileSync(new URL(image.href.replace(/\.png$/,'.json'))));
   assert.equal(metadata.id,id);assert.equal(metadata.edition,e);assert.equal(metadata.color_mood,edition.mood);
   if(metadata.artwork_sha256)assert.equal(createHash('sha256').update(readFileSync(image)).digest('hex'),metadata.artwork_sha256);
  }
 }
});
test('latest approved islands each appear once as a pair in the gallery',()=>{
 for(const id of ['000012','000013','000014']){
  const pair=editions.filter(x=>x.islandId===id);assert.equal(pair.length,2);
  for(const edition of pair)assert.ok(edition.image.includes('/v20261126/'));
 }
});
test('approved batch through Rapa Nui is complete and uses reviewed assets',()=>{
 assert.equal(editions.length,126);
 for(let n=15;n<=25;n++){
  const id=String(n).padStart(6,'0'),pair=editions.filter(x=>x.islandId===id);
  assert.equal(pair.length,2);
  for(const e of pair)assert.ok(e.image.includes('/geography-20261126/'));
 }
});

test('collection through island 50 includes every unique N/S pair',()=>{
 for(let n=26;n<=50;n++){const id=String(n).padStart(6,'0');const pair=editions.filter(e=>e.islandId===id);assert.equal(pair.length,2);for(const e of pair)assert.ok(e.image.includes('/collection-20261126/'));}
});

test('freshwater collection preserves each island type and 26 distinct backgrounds',()=>{
 const backgrounds=new Set();
 for(let n=51;n<=63;n++){
  const id=String(n).padStart(6,'0'),pair=editions.filter(e=>e.islandId===id);
  assert.equal(pair.length,2);
  assert.equal(traits[pair[0].name][2],'Freshwater');
  assert.equal(traits[pair[0].name][1],n>=61?'River Island':'Lake Island');
  for(const edition of pair){
   const metadata=JSON.parse(readFileSync(new URL('../public'+edition.image.replace(/\.png$/,'.json'),import.meta.url)));
   assert.equal(metadata.water_type,'Freshwater');
   assert.equal(metadata.orientation_degrees,edition.id.endsWith('-N')?0:180);
   backgrounds.add(metadata.background);
  }
 }
 assert.equal(backgrounds.size,26);
});

test('freshwater aliases collapse into their curated island without hiding nearby islands',()=>{
 const aliases=value('curatedGeoNamesIds');
 const global=JSON.parse(readFileSync(new URL('../public/data/world-islands.json',import.meta.url)));
 assert.equal(new Set(aliases).size,14);
 for(const id of aliases){
  const item=global.find(x=>x.sourceId===id);assert.ok(item,id);
  assert.ok(registry.some(r=>Number(ids[r[0]])>=51&&Math.abs(r[3]-item.latitude)<.3&&Math.abs(r[4]-item.longitude)<.3),id);
 }
 assert.ok(aliases.includes('geonames:3470986'));
 for(const id of ['geonames:12966122','geonames:3406525','geonames:3470985','geonames:930473'])assert.ok(!aliases.includes(id));
});

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

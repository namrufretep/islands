import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=path=>JSON.parse(readFileSync(new URL('../'+path,import.meta.url),'utf8'));
const world=read('public/data/world-islands.json'),review=read('public/data/island-index-review.json');
test('audit preserves every original ID and suppresses only localized same-name matches',()=>{
 assert.equal(world.length,166980);assert.equal(review.sourceRecords,world.length);
 const byId=new Map(world.map(r=>[r.sourceId,r]));assert.equal(byId.size,world.length);
 for(const [source,target] of Object.entries(review.duplicateOf)){
  const a=byId.get(source),b=byId.get(target);assert.ok(a&&b);assert.equal(a.countryCode,b.countryCode);const normalized=s=>s.normalize('NFKD').toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');assert.equal(normalized(a.name),normalized(b.name));
  assert.ok(Math.abs(a.latitude-b.latitude)<.003);assert.ok(!review.duplicateOf[target]);
 }
 for(const id of ['geonames:3379591','geonames:3661405']){assert.equal(byId.get(id).name,'Baboon Island');assert.equal(review.duplicateOf[id],undefined)}
});
test('all area shards contain finite sourced estimates; report matches actual coverage',()=>{
 let count=0;const ids=new Set(world.map(r=>r.sourceId));
 for(let shard=0;shard<32;shard++){
  const data=read('public/data/island-details/'+shard+'.json');assert.equal(data.source,'GSHHG 2.3.7');
  for(const [id,f] of Object.entries(data.records)){
   assert.ok(ids.has('geonames:'+id));assert.equal(Number(id)%32,shard);assert.ok(Number.isFinite(f.areaKm2)&&f.areaKm2>0);assert.match(f.shorelineId,/^[13]:/);assert.ok(!/^1:[0-6]$/.test(f.shorelineId));count++;
  }
 }
 assert.equal(count,read('docs/index-data-review.json').approximate_areas_published);
 assert.ok(count>30000);assert.equal(Object.keys(review.curated).length,212);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const value=name=>JSON.parse(source.match(new RegExp('const '+name+'=(.*?);'))[1]);
const editions=value('previewEditions');
for(const batch of ['000101-000126','000127-000152']){
const config=JSON.parse(readFileSync(new URL(`../data/collections/alphabet-${batch}/geography-validation.json`,import.meta.url)));
test(`A–Z batch ${batch} covers every initial once and preserves 52 independently rendered editions`,()=>{
 assert.deepEqual(config.map(c=>c.letter),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''));
 const backgrounds=new Set();
 for(const c of config){
  assert.equal(c.name[0].toUpperCase(),c.letter);
  assert.equal(value('registry').filter(r=>r[0]===c.name).length,1);
  assert.ok(value('curatedGeoNamesIds').includes(c.source_id));
  assert.ok(c.reference_checked);assert.equal(c.political_boundaries,false);assert.ok(c.area_km2>0);
  const pair=editions.filter(e=>e.islandId===c.id);assert.equal(pair.length,2);
  const hashes=[];
  for(const e of pair){
   const image=new URL('../public'+e.image,import.meta.url);
   const meta=JSON.parse(readFileSync(new URL(image.href.replace(/\.png$/,'.json'))));
   assert.equal(meta.canvas_px,2048);assert.equal(meta.dpi_target,300);assert.ok(meta.land_coverage_fraction>=.995);
   assert.equal(meta.orientation_degrees,e.id.endsWith('-S')?180:0);
   assert.equal(createHash('sha256').update(readFileSync(image)).digest('hex'),meta.artwork_sha256);
   backgrounds.add(meta.background);hashes.push(meta.artwork_sha256);
  }
  assert.notEqual(hashes[0],hashes[1]);
 }
 assert.equal(backgrounds.size,52);
});
}

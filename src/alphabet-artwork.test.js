import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
const value=name=>JSON.parse(source.match(new RegExp('const '+name+'=(.*?);'))[1]);
const editions=value('previewEditions');
for(const batch of ['000101-000126','000127-000152','000153-000178','000179-000204','000205-000230','000231-000256','000257-000308']){
const config=JSON.parse(readFileSync(new URL(`../data/collections/alphabet-${batch}/geography-validation.json`,import.meta.url)));
const chromatic=batch==='000257-000308';
test(`A–Z batch ${batch} preserves its alphabet cycles and independent editions`,()=>{
 assert.deepEqual(config.map(c=>c.letter),'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.repeat(chromatic?2:1).split(''));
 const backgrounds=new Set(),directions=new Set();
 for(const c of config){
  assert.equal(c.name[0].toUpperCase(),c.letter);
  assert.equal(value('registry').filter(r=>r[0]===c.name).length,1);
  assert.ok(value('curatedGeoNamesIds').includes(c.source_id));
  for(const alias of c.source_aliases||[])assert.ok(value('curatedGeoNamesIds').includes(alias));
  assert.ok(c.reference_checked);assert.equal(c.political_boundaries,false);assert.ok(c.area_km2>0);
  const pair=editions.filter(e=>e.islandId===c.id);assert.equal(pair.length,2);
  const hashes=[];
  for(const e of pair){
   const image=new URL('../public'+e.image,import.meta.url);
   const meta=JSON.parse(readFileSync(new URL(image.href.replace(/\.png$/,'.json'))));
   if(batch==='000179-000204'){assert.equal(meta.render_style,'bouvet-original');assert.equal(meta.art_version,'4.6-bouvet');assert.equal(meta.style_reference.island_id,'000001');}
   if(['000205-000230','000231-000256','000257-000308'].includes(batch)){
    const design=c.lighting_design[e.id.endsWith('-S')?'S':'N'];
    assert.equal(meta.art_version,chromatic?'4.8-bouvet-chromatic':'4.7-bouvet-directional');assert.equal(meta.variable_lighting,true);
    assert.equal(meta.lighting.azimuth_degrees,design.azimuth_degrees);assert.equal(meta.lighting.elevation_degrees,design.elevation_degrees);
    const [lx,ly]=meta.lighting.horizontal_light_vector,[sx,sy]=meta.lighting.shadow_offset_px;
    assert.ok(lx*sx+ly*sy<0,'cast shadow must point away from light');directions.add(meta.lighting.azimuth_degrees);
   }
   if(chromatic){
    assert.equal(meta.render_style,'bouvet-original');
    assert.ok(meta.palette.length>=7&&meta.palette.length<=10);
    assert.equal(meta.palette_stop_count,meta.palette.length);
    assert.equal(meta.chromatic_artistic_field,true);
    assert.equal(meta.chromatic_model_revision,3);
   }
   assert.equal(meta.canvas_px,2048);assert.equal(meta.dpi_target,300);assert.ok(meta.land_coverage_fraction>=.995);
   assert.equal(meta.orientation_degrees,e.id.endsWith('-S')?180:0);
   assert.equal(createHash('sha256').update(readFileSync(image)).digest('hex'),meta.artwork_sha256);
   backgrounds.add(meta.background);hashes.push(meta.artwork_sha256);
  }
  assert.notEqual(hashes[0],hashes[1]);
 }
 assert.equal(backgrounds.size,config.length*2);
 if(['000205-000230','000231-000256','000257-000308'].includes(batch))assert.equal(directions.size,8);
});
}

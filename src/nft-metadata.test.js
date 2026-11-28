import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';

const read=name=>JSON.parse(readFileSync(new URL(`../public/nft/${name}.json`,import.meta.url)));
test('every prepared NFT metadata URI resolves to the intended original and its traits',()=>{
 const manifest=read('manifest');assert.equal(manifest.editions.length,408);assert.equal(manifest.release_status,'not_released');
 for(const entry of manifest.editions){
  const metadata=read(entry.artwork_id),image=new URL(metadata.image);
  assert.equal(image.protocol,'https:');assert.equal(image.origin,'https://islands-kappa.vercel.app');
  const path=new URL('../public'+image.pathname,import.meta.url);assert.ok(existsSync(path));
  assert.equal(createHash('sha256').update(readFileSync(path)).digest('hex'),entry.image_sha256);
  assert.ok(metadata.name.includes(entry.artwork_id));assert.ok(metadata.description.length>20);
  const traits=Object.fromEntries(metadata.attributes.map(t=>[t.trait_type,t.value]));
  assert.equal(traits['Artwork ID'],entry.artwork_id);
  assert.equal(traits.Orientation,entry.artwork_id.endsWith('-N')?'North-Up':'South-Up');
  assert.equal(new URL(metadata.external_url).searchParams.get('edition'),entry.artwork_id);
 }
});
test('collection metadata declares the preferred 10% recipient without claiming enforcement',()=>{
 const collection=read('collection'),manifest=read('manifest');
 assert.equal(collection.seller_fee_basis_points,1000);
 assert.equal(collection.fee_recipient,'0xfc5708cb64604dcf6f62de5d63a051ed577e10c1');
 assert.equal(manifest.creator_fee_enforcement,'not_configured');
});

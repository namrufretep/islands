import test from 'node:test';
import assert from 'node:assert/strict';
import {galleryInventory} from './gallery-inventory.js';
test('public gallery contains only confirmed minted editions, never unreleased placeholders',()=>{
 const previews=[{id:'000001-N',status:'Preview'}];
 const published=[{id:'000002-N',status:'Collected'}, {id:'000003-N',chain:{verified:false,minted:true}},{id:'000004-N',chain:{verified:true,minted:false}},{id:'000005-N',chain:{verified:true,minted:true}}];
 assert.deepEqual(galleryInventory(published,previews).map(e=>e.id),['000005-N']);
 assert.equal(galleryInventory([],previews).length,0);
 assert.equal(galleryInventory(published,previews,{administrator:true}).length,5);
});
test('administrator sees all prepared artwork while published metadata wins ID collisions',()=>{
 const preview={id:'000001-N',status:'Preview'},minted={id:'000001-N',chain:{verified:true,minted:true}};
 assert.deepEqual(galleryInventory([minted],[preview],{administrator:true}),[minted]);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import {editionStatus} from './edition-status.js';
const minter='0x1111111111111111111111111111111111111111';
const owner='0x2222222222222222222222222222222222222222';

test('existing preview artwork is not a minted NFT',()=>{
 const state=editionStatus({artworkExists:true,collectionReleased:false});
 assert.equal(state.artwork,'Exists');assert.equal(state.mint,'Not minted');
 assert.equal(state.mintedBy,'—');assert.equal(state.ownedBy,'—');
});
test('a registry island without artwork has a separate artwork status',()=>{
 const state=editionStatus({artworkExists:false,collectionReleased:false});
 assert.equal(state.artwork,'Not existing');assert.equal(state.mint,'Not minted');
});
test('missing or unverified chain data never invents a minter or owner',()=>{
 for(const chain of [null,{verified:false,minted:true,mintedBy:minter,ownedBy:owner}]){
  const state=editionStatus({artworkExists:true,collectionReleased:true,chain});
  assert.equal(state.mint,'Not verified');assert.equal(state.mintedBy,'Not verified');
  assert.equal(state.ownedByAddress,null);assert.equal(state.ownedBy,'Not verified');
 }
 assert.equal(editionStatus({artworkExists:true}).mint,'Not verified');
});
test('verified mint history and current ownership can refer to different wallets',()=>{
 const state=editionStatus({artworkExists:true,collectionReleased:true,chain:{verified:true,minted:true,mintedBy:minter,ownedBy:owner}});
 assert.equal(state.mint,'Minted');assert.equal(state.mintedByAddress,minter);
 assert.equal(state.ownedByAddress,owner);assert.notEqual(state.mintedBy,state.ownedBy);
});
test('unknown minter stays unknown even when the current owner is verified',()=>{
 const state=editionStatus({artworkExists:true,collectionReleased:true,chain:{verified:true,minted:true,ownedBy:owner}});
 assert.equal(state.mintedBy,'Not verified');assert.equal(state.mintedByAddress,null);
 assert.equal(state.ownedByAddress,owner);
});

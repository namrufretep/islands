import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {canonicalTokenId,directPriceForStake,stakingQuoteTypedData} from './launch-config.js';
import {hashTypedData} from 'viem';

test('canonical allocation gives two unique independent slots and permits future expansion',()=>{
 const ids=new Set();for(let island=1;island<=500;island++)for(const orientation of ['N','S'])ids.add(canonicalTokenId(String(island).padStart(6,'0')+'-'+orientation));
 assert.equal(ids.size,1000);assert.equal(canonicalTokenId('000001-N'),1);assert.equal(canonicalTokenId('000001-S'),2);
 for(const bad of ['000000-N','000001-X','1-N','000001-N-extra'])assert.throws(()=>canonicalTokenId(bad));
});
test('staking tiers use the direct price, including exact threshold boundaries',()=>{
 for(const [keys,price] of [[0,750000],[1,712500],[4,712500],[5,675000],[14,675000],[15,637500],[29,637500],[30,600000],[49,600000],[50,562500]])assert.equal(directPriceForStake(keys),BigInt(price)*10n**18n);
 assert.throws(()=>directPriceForStake(-1));
});
test('released-plan candidate hashes match every actual metadata file and artwork',()=>{
 const plan=JSON.parse(readFileSync(new URL('../public/launch/release-plan.json',import.meta.url)));
 assert.equal(plan.status,'preparation_only');assert.equal(plan.collection_address,null);assert.equal(plan.target_islands,500);assert.equal(plan.prepared_editions,200);
 for(const e of plan.editions){
  assert.equal(e.release_status,'not_released');assert.equal(e.token_id,canonicalTokenId(e.artwork_id));
  const metadata=readFileSync(new URL('../public'+new URL(e.metadata_uri).pathname,import.meta.url));
  assert.equal(createHash('sha256').update(metadata).digest('hex'),e.metadata_sha256);
  const image=readFileSync(new URL('../public'+new URL(e.image_url).pathname,import.meta.url));
  assert.equal(createHash('sha256').update(image).digest('hex'),e.image_sha256);
 }
});
test('signed eligibility is bound to contract, chain and recipient',()=>{
 const message={payer:'0x00000000000000000000000000000000000a11ce',recipient:'0x0000000000000000000000000000000000000b0b',tokenId:1n,basePrice:750000n*10n**18n,stakedKeys:50n,stakeBlock:999n,issuedAt:1000n,deadline:1300n,nonce:0n,verifierVersion:1n,metadataHash:'0x'+'12'.repeat(32)};
 const original=stakingQuoteTypedData('0x0000000000000000000000000000000000001234',message);
 const hash=hashTypedData(original);
 assert.notEqual(hash,hashTypedData({...original,message:{...message,recipient:message.payer}}));
 assert.notEqual(hash,hashTypedData({...original,domain:{...original.domain,chainId:84532}}));
 assert.notEqual(hash,hashTypedData(stakingQuoteTypedData('0x0000000000000000000000000000000000005678',message)));
});

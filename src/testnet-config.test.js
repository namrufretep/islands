import test from 'node:test';
import assert from 'node:assert/strict';
import {assertTestChain,deploymentMatches,validTransactionHash,TEST_PRICE,TEST_METADATA,TEST_TOKEN_ID} from './testnet-config.js';
test('test actions reject mainnet and every other chain before submitting',()=>{
 for(const chain of [84532,'84532','0x14a34'])assert.doesNotThrow(()=>assertTestChain(chain));
 for(const chain of [8453,'0x2105',1,11155111,undefined,'garbage'])assert.throws(()=>assertTestChain(chain));
});
test('saved deployment is trusted only after matching successful creation receipt and exact bytecode',()=>{
 const receipt={status:'success',contractAddress:'0x'+'1'.repeat(40)},transaction={to:null,input:'0x60006000'};
 assert.equal(deploymentMatches(transaction,receipt,'0x60006000'),true);
 assert.equal(deploymentMatches({...transaction,to:'0x'+'2'.repeat(40)},receipt,'0x60006000'),false);
 assert.equal(deploymentMatches(transaction,{...receipt,status:'reverted'},'0x60006000'),false);
 assert.equal(deploymentMatches(transaction,receipt,'0x60006001'),false);
 assert.equal(deploymentMatches(transaction,{...receipt,contractAddress:null},'0x60006000'),false);
});
test('test price and metadata are independent from real edition IDs and real KEY',()=>{
 assert.equal(TEST_PRICE,750000000000000000000000n);assert.equal(TEST_TOKEN_ID,1n);
 assert.ok(TEST_METADATA.includes('/testnet/'));assert.ok(!TEST_METADATA.includes('/nft/'));
 assert.equal(validTransactionHash('0x'+'f'.repeat(64)),true);assert.equal(validTransactionHash('invalid'),false);
});

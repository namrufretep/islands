import test from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {verifyMessage} from 'viem';
import {privateKeyToAccount} from 'viem/accounts';
import {administratorWallet,createAdminPreview} from './admin-preview.js';
// Fixture signer is deliberately NOT the creator: a real signature from another
// wallet must still fail even if the provider claims the administrator address.
const stranger=privateKeyToAccount('0x'+'11'.repeat(32));
function setup(verify=async()=>true){
 let time=100000,timer;
 const provider=new EventEmitter();provider.accounts=[administratorWallet];provider.calls=[];
 provider.request=async({method,params})=>{provider.calls.push({method,params});if(method==='eth_accounts')return provider.accounts;if(method==='personal_sign')return '0x1234';throw Error('Unexpected '+method)};
 const admin=createAdminPreview({verify,origin:'https://islands-kappa.vercel.app',nonce:()=> 'test-nonce',now:()=>time,schedule:callback=>{timer=callback;return 1},cancel:()=>{timer=null}});
 admin.bind(provider,provider.accounts);
 return {admin,provider,advance:ms=>{time+=ms;timer?.()}};
}
test('creator preview asks for a scoped read-only signature, exits and expires',async()=>{
 let payload;
 const f=setup(async p=>{payload=p;return true});
 assert.deepEqual(f.admin.state(),{eligible:true,active:false,busy:false});
 await f.admin.enter();assert.equal(f.admin.state().active,true);
 assert.match(payload.message,/https:\/\/islands-kappa.vercel.app/);assert.match(payload.message,/No transaction, token approval or transfer/);assert.match(payload.message,/test-nonce/);
 assert.deepEqual(f.provider.calls.map(c=>c.method),['eth_accounts','personal_sign','eth_accounts']);
 f.admin.exit();assert.equal(f.admin.state().active,false);await f.admin.enter();f.advance(1800000);assert.equal(f.admin.state().active,false);
});
test('another connected address never receives administrator access',async()=>{
 const {admin,provider}=setup();provider.accounts=[stranger.address];provider.emit('accountsChanged',provider.accounts);
 assert.equal(admin.state().eligible,false);await assert.rejects(admin.enter(),/administrator wallet/);assert.equal(provider.calls.length,0);
});
test('provider claiming creator address cannot bypass a real signature check',async()=>{
 const f=setup(payload=>verifyMessage(payload));
 f.provider.request=async({method,params})=>method==='eth_accounts'?[administratorWallet]:stranger.signMessage({message:{raw:params[0]}});
 await assert.rejects(f.admin.enter(),/could not be verified/);assert.equal(f.admin.state().active,false);
});
test('wallet changes during verification invalidate the pending signature',async()=>{
 let finish;const f=setup(()=>new Promise(resolve=>{finish=resolve}));
 const attempt=f.admin.enter();while(!finish)await Promise.resolve();f.provider.accounts=[stranger.address];f.provider.emit('accountsChanged',f.provider.accounts);finish(true);
 await assert.rejects(attempt,/Wallet changed/);assert.equal(f.admin.state().active,false);assert.equal(f.admin.state().eligible,false);
});
test('disconnect and chain changes revoke an active preview; cancellation stays closed',async()=>{
 const f=setup();await f.admin.enter();f.provider.emit('chainChanged','0x1');assert.equal(f.admin.state().active,false);
 await f.admin.enter();f.provider.emit('disconnect');assert.equal(f.admin.state().active,false);assert.equal(f.admin.state().eligible,false);
 const g=setup();g.provider.request=async({method})=>{if(method==='eth_accounts')return [administratorWallet];throw Error('User rejected signature')};
 await assert.rejects(g.admin.enter(),/rejected/);assert.equal(g.admin.state().active,false);assert.equal(g.admin.state().busy,false);
});

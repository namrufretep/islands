import test from 'node:test';
import assert from 'node:assert/strict';
import {resolveFarcasterProvider,requestWalletAccounts,farcasterLaunchUrl,walletError} from './wallet-connection.js';
const provider={request:async()=>['0x'+'12'.repeat(20)]};
const sdk=options=>({isInMiniApp:async()=>true,actions:{ready:()=>new Promise(()=>{})},wallet:{getEthereumProvider:async()=>provider},...options});
test('Farcaster wallet connection does not wait for a hanging splash ready call',async()=>{
 const result=await resolveFarcasterProvider(sdk(),{timeout:20});assert.equal(result,provider);assert.equal((await requestWalletAccounts(result)).length,1);
});
test('retry rechecks host context instead of keeping an early false result',async()=>{
 let inside=false;const host=sdk({isInMiniApp:async()=>inside});
 await assert.rejects(resolveFarcasterProvider(host,{timeout:20}),/Open ISLANDS as a Farcaster Mini App/);
 inside=true;assert.equal(await resolveFarcasterProvider(host,{timeout:20}),provider);
});
test('older host with hanging capability discovery uses its Farcaster wallet bridge',async()=>{
 const host=sdk({wallet:{getEthereumProvider:()=>new Promise(()=>{}),ethProvider:provider}});
 assert.equal(await resolveFarcasterProvider(host,{timeout:10}),provider);
});
test('unsupported host and denied requests remain actionable and do not invent a wallet',async()=>{
 await assert.rejects(resolveFarcasterProvider(sdk({wallet:{getEthereumProvider:async()=>undefined}}),{timeout:20}),/does not offer/);
 await assert.rejects(requestWalletAccounts({request:async()=>[]}),/No wallet account/);
 assert.match(walletError({code:4001}),/cancelled/);assert.match(walletError({code:-32002}),/already open/);
});
test('outside-browser launch link opens the exact Islands domain in Farcaster',()=>{
 const url=new URL(farcasterLaunchUrl('https://islands-kappa.vercel.app/?edition=000057-N'));
 assert.equal(url.origin,'https://farcaster.xyz');assert.equal(url.pathname,'/~/mini-apps/launch');assert.equal(url.searchParams.get('domain'),'islands-kappa.vercel.app');
});
test('root page is a Mini App embed and the referenced identity images exist',async()=>{
 const {readFile}=await import('node:fs/promises');
 const html=await readFile(new URL('../index.html',import.meta.url),'utf8');
 const embed=JSON.parse(html.match(/name="fc:miniapp" content='([^']+)'/)[1]);
 assert.equal(embed.button.action.type,'launch_miniapp');assert.equal(embed.button.action.url,'https://islands-kappa.vercel.app/');
 for(const path of ['/app-preview.png','/icon.png'])assert.ok((await readFile(new URL('../public'+path,import.meta.url))).length>100);
});

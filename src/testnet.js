import {createPublicClient,createWalletClient,http,custom,formatEther,formatUnits,keccak256,stringToHex,parseEventLogs,erc20Abi} from 'viem';
import {baseSepolia} from 'viem/chains';
import {sdk} from '@farcaster/miniapp-sdk';
import {resolveFarcasterProvider,requestWalletAccounts,withTimeout} from './wallet-connection.js';
import {TEST_CHAIN_ID,TEST_CHAIN_HEX,TEST_PRICE,TEST_TOKEN_ID,TEST_METADATA,TEST_RPC,TEST_EXPLORER,assertTestChain,deploymentMatches,validTransactionHash} from './testnet-config.js';
import './style.css';
import './impossible-atlas.css';
import './testnet.css';

const root=document.querySelector('#app');
root.innerHTML=`<main class="testnet-page">
<header><div class="brand">ISLANDS<small>TEST MINT · BASE SEPOLIA</small></div><a href="/">Back to ISLANDS</a></header>
<section class="page">
<p class="testnet-banner">TEST ONLY · Network 84532 · No real island edition</p>
<h1>Test your first mint</h1>
<p>This separate environment uses free test KEY and a clearly marked test NFT. It does not mint or reserve any original island.</p>
<article class="panel"><h2>1 · Connect on Base Sepolia</h2>
<p>Choose a wallet that supports the Base Sepolia test network. Wallet confirmations are required for every transaction.</p>
<div class="testnet-buttons"><button id="browserConnect" class="outline">Connect browser wallet</button><button id="farcasterConnect" class="outline">Connect Farcaster wallet</button></div>
<p id="walletState">No wallet connected.</p>
<dl class="testnet-facts"><dt>Test ETH for fees</dt><dd id="ethBalance">—</dd><dt>Test KEY balance</dt><dd id="keyBalance">—</dd></dl>
<p>Get free Base Sepolia test ETH through a faucet listed by Base. Do not purchase or bridge real funds for this test.</p>
<a href="https://docs.base.org/get-started/get-funds#testnet-base-sepolia" target="_blank" rel="noopener noreferrer">Official test ETH faucets ↗</a>
<button id="refresh" class="outline" disabled>Refresh balances</button></article>
<article class="panel"><h2>2 · Create your test environment</h2>
<p>One confirmation creates your separate test KEY, NFT collection and test treasury. You receive 1,000,000 test KEY. Only test ETH gas is used.</p>
<button id="deploy" class="primary" disabled>Create test environment</button>
<p id="deploymentState">Not deployed yet.</p><div id="contractLinks"></div>
</article>
<article class="panel"><h2>3 · Mint the test NFT</h2>
<img class="testnet-art" src="/testnet/test-only.svg" alt="ISLANDS TEST ONLY — Base Sepolia; not a real collection edition">
<p>Test Edition 1 · Direct price: <strong>750,000 test KEY</strong></p>
<p>First approve exactly this test amount, then mint. This test has no staking discount.</p>
<div class="testnet-buttons"><button id="approve" class="outline" disabled>1 · Approve 750,000 test KEY</button><button id="mint" class="primary" disabled>2 · Mint test NFT</button></div>
<button id="faucet" class="outline" disabled>Get more free test KEY</button>
<p id="mintState">Create your test environment first.</p>
<div id="mintResult" aria-live="polite"></div>
</article>
<p id="testStatus" role="status" aria-live="polite">Loading test contracts…</p>
<article class="panel"><h2>Confirmed transactions</h2><ul id="transactions"><li>No transactions sent yet.</li></ul></article>
</section></main>`;
const $=id=>document.getElementById(id);
const publicClient=createPublicClient({chain:baseSepolia,transport:http(TEST_RPC)});
let artifacts=null,provider=null,walletClient=null,account=null,suite=null,busy=false,gas=0n,available=false,allowance=0n,balance=0n,owner=null,generation=0,detach=()=>{};
const zeroAddress='0x0000000000000000000000000000000000000000';
const same=(a,b)=>typeof a==='string'&&typeof b==='string'&&a.toLowerCase()===b.toLowerCase();
const storageKey=address=>'islands:testnet:84532:suite:'+address.toLowerCase();
function status(message){$('testStatus').textContent=message;}
function buttons(){
 $('browserConnect').disabled=$('farcasterConnect').disabled=busy;
 $('refresh').disabled=busy||!account;
 $('deploy').disabled=busy||!account||!artifacts||gas===0n;
 $('deploy').textContent=suite?'Create a fresh test environment':'Create test environment';
 $('approve').disabled=busy||!suite||!account||!available||balance<TEST_PRICE||allowance>=TEST_PRICE||gas===0n;
 $('mint').disabled=busy||!suite||!account||!available||balance<TEST_PRICE||allowance<TEST_PRICE||gas===0n;
 $('faucet').disabled=busy||!suite||!account||gas===0n;
}
function link(parent,label,url){const a=document.createElement('a');a.textContent=label;a.href=url;a.target='_blank';a.rel='noopener noreferrer';parent.append(a);}
function logTransaction(label,hash){
 const list=$('transactions');if(!list.dataset.hasEntries){list.replaceChildren();list.dataset.hasEntries='true';}
 let row=[...list.children].find(item=>item.dataset.transactionHash===hash);
 if(!row){row=document.createElement('li');row.dataset.transactionHash=hash;list.prepend(row);}
 row.replaceChildren();link(row,label+' ↗',TEST_EXPLORER+'/tx/'+hash);
}
function resetConnection(){
 generation++;detach();detach=()=>{};account=null;suite=null;walletClient=null;provider=null;gas=0n;available=false;owner=null;allowance=balance=0n;
 $('walletState').textContent='Wallet account or network changed. Connect again on Base Sepolia.';
 $('ethBalance').textContent=$('keyBalance').textContent='—';$('deploymentState').textContent='Connect to restore your test environment.';
 $('mintState').textContent='No active test environment.';$('mintResult').replaceChildren();$('contractLinks').replaceChildren();buttons();
}
async function assertWallet(){
 if(!account||!provider||!walletClient)throw Error('Connect a testnet-compatible wallet first.');
 assertTestChain(await provider.request({method:'eth_chainId'}));
 const accounts=await provider.request({method:'eth_accounts'});
 if(!same(accounts?.[0],account))throw Error('Wallet account changed. Reconnect before continuing.');
}
async function run(action){
 if(busy)return;busy=true;buttons();const version=generation;
 try{await action(version);}
 catch(error){status(error?.code===4001?'Wallet request cancelled. You can retry.':(error?.shortMessage||error?.message||'Request failed. Please retry.').slice(0,350));}
 finally{busy=false;buttons();}
}
async function receipt(hash,label){
 if(!validTransactionHash(hash))throw Error('Wallet returned an invalid transaction reference.');
 logTransaction(label+' · pending',hash);status('Waiting for confirmation on Base Sepolia…');
 const result=await publicClient.waitForTransactionReceipt({hash,confirmations:1,timeout:120000});
 if(result.status!=='success')throw Error('The test transaction reverted. No mint success is being recorded.');
 logTransaction(label+' · confirmed',hash);return result;
}
function contractLinks(){
 const out=$('contractLinks');out.replaceChildren();
 for(const [label,address] of [['Test KEY',suite.key],['Test collection',suite.collection],['Test treasury',suite.treasury]])link(out,label+' ↗',TEST_EXPLORER+'/address/'+address);
}
async function loadSuite(hash,version){
 if(!artifacts||!validTransactionHash(hash))throw Error('Invalid test deployment reference.');
 const [transaction,proof]=await Promise.all([publicClient.getTransaction({hash}),publicClient.getTransactionReceipt({hash})]);
 if(!deploymentMatches(transaction,proof,artifacts.suite.bytecode))throw Error('Saved deployment does not match this checked test build. Create a fresh test environment.');
 const address=proof.contractAddress;
 const read=functionName=>publicClient.readContract({address,abi:artifacts.suite.abi,functionName});
 const [versionName,key,collection,treasury]=await Promise.all([read('VERSION'),read('key'),read('collection'),read('treasury')]);
 if(versionName!=='ISLANDS_TESTNET_V1')throw Error('Unexpected test environment.');
 const [tokenKey,payout,name,decimals]=await Promise.all([
  publicClient.readContract({address:collection,abi:artifacts.collection.abi,functionName:'KEY'}),
  publicClient.readContract({address:collection,abi:artifacts.collection.abi,functionName:'MINT_PROCEEDS_RECIPIENT'}),
  publicClient.readContract({address:collection,abi:artifacts.collection.abi,functionName:'name'}),
  publicClient.readContract({address:key,abi:artifacts.key.abi,functionName:'decimals'})
 ]);
 if(!same(tokenKey,key)||!same(payout,treasury)||same(key,zeroAddress)||name!=='ISLANDS TEST ONLY'||Number(decimals)!==18)throw Error('Test deployment configuration mismatch.');
 if(version!==generation)throw Error('Wallet changed during verification. Connect again.');
 suite={address,key,collection,treasury};contractLinks();$('deploymentState').textContent='Separate test environment verified on Base Sepolia.';
}
async function refreshState(version=generation){
 await assertWallet();const address=account;
 const nextGas=await publicClient.getBalance({address});
 if(version!==generation)return;gas=nextGas;$('ethBalance').textContent=formatEther(gas)+' test ETH';
 if(!suite){buttons();return;}
 const selectedSuite=suite;
 const [nextBalance,nextAllowance,offer,enabled]=await Promise.all([
  publicClient.readContract({address:suite.key,abi:artifacts.key.abi,functionName:'balanceOf',args:[address]}),
  publicClient.readContract({address:suite.key,abi:artifacts.key.abi,functionName:'allowance',args:[address,suite.collection]}),
  publicClient.readContract({address:suite.collection,abi:artifacts.collection.abi,functionName:'mintOffers',args:[TEST_TOKEN_ID]}),
  publicClient.readContract({address:suite.collection,abi:artifacts.collection.abi,functionName:'keyMintEnabled'})
 ]);
 if(version!==generation||selectedSuite!==suite)return;
 balance=nextBalance;allowance=nextAllowance;available=enabled===true&&offer[0]===TEST_PRICE&&offer[1]===TEST_METADATA;owner=null;
 $('keyBalance').textContent=formatUnits(balance,18)+' test KEY';
 if(offer[0]===0n){
  try{owner=await publicClient.readContract({address:suite.collection,abi:artifacts.collection.abi,functionName:'ownerOf',args:[TEST_TOKEN_ID]});}
  catch{owner=null;}
  if(version!==generation||selectedSuite!==suite)return;
 }
 $('mintState').textContent=owner?'Test Edition 1 is minted. Current owner: '+owner:!available?'Test edition is not available. Create a fresh test environment.':balance<TEST_PRICE?'Get more free test KEY before minting.':allowance<TEST_PRICE?'Ready: approve exactly 750,000 test KEY, then mint.':'Approval confirmed. Ready to mint Test Edition 1.';
 buttons();
}
async function connect(source){
 const chosen=source==='browser'?window.ethereum:await resolveFarcasterProvider(sdk);
 if(!chosen)throw Error('No browser wallet detected. Open this page in a browser with a wallet extension, or in your wallet’s browser.');
 if(source==='farcaster'&&sdk.getChains){
  const chains=await withTimeout(sdk.getChains(),5000,'Could not check supported Farcaster networks.');
  if(!chains.includes('eip155:84532'))throw Error('This Farcaster wallet does not support Base Sepolia. Use a browser wallet for this test.');
 }
 const accounts=await requestWalletAccounts(chosen);
 try{await chosen.request({method:'wallet_switchEthereumChain',params:[{chainId:TEST_CHAIN_HEX}]});}
 catch(error){
  if(error.code!==4902&&error?.data?.originalError?.code!==4902)throw error;
  await chosen.request({method:'wallet_addEthereumChain',params:[{chainId:TEST_CHAIN_HEX,chainName:'Base Sepolia',nativeCurrency:{name:'Test Ether',symbol:'ETH',decimals:18},rpcUrls:[TEST_RPC],blockExplorerUrls:[TEST_EXPLORER]}]});
  await chosen.request({method:'wallet_switchEthereumChain',params:[{chainId:TEST_CHAIN_HEX}]});
 }
 assertTestChain(await chosen.request({method:'eth_chainId'}));
 detach();generation++;const version=generation;provider=chosen;account=accounts[0];suite=null;gas=0n;available=false;balance=allowance=0n;
 walletClient=createWalletClient({account,chain:baseSepolia,transport:custom(provider)});
 const changed=()=>resetConnection();provider.on?.('accountsChanged',changed);provider.on?.('chainChanged',changed);provider.on?.('disconnect',changed);
 detach=()=>{chosen.removeListener?.('accountsChanged',changed);chosen.removeListener?.('chainChanged',changed);chosen.removeListener?.('disconnect',changed);};
 $('walletState').textContent='Connected: '+account+' · Base Sepolia (84532)';
 $('mintResult').replaceChildren();$('contractLinks').replaceChildren();$('keyBalance').textContent='Create a test environment first.';
 await refreshState(version);
 let saved=null;try{saved=localStorage.getItem(storageKey(account));}catch{}
 if(saved&&artifacts){try{await loadSuite(saved,version);await refreshState(version);}catch(error){suite=null;$('deploymentState').textContent=error.message;}}
 status(gas===0n?'Get free Base Sepolia test ETH, then refresh balances.':'Wallet connected on the test network. No transaction was sent.');buttons();
}
$('browserConnect').onclick=()=>run(()=>connect('browser'));
$('farcasterConnect').onclick=()=>run(()=>connect('farcaster'));
$('refresh').onclick=()=>run(async version=>{await refreshState(version);status('Testnet balances refreshed.');});
$('deploy').onclick=()=>run(async version=>{
 await assertWallet();if(!artifacts)throw Error('Compiled test contracts are not ready yet.');
 const buyer=account;status('Confirm creation of the separate test environment in your wallet.');
 const hash=await walletClient.deployContract({account:buyer,chain:baseSepolia,abi:artifacts.suite.abi,bytecode:artifacts.suite.bytecode});
 await receipt(hash,'Create test environment');
 if(version!==generation)throw Error('Wallet changed. Your confirmed deployment remains available in the transaction history.');
 await loadSuite(hash,version);
 try{localStorage.setItem(storageKey(buyer),hash);}catch{}
 $('mintResult').replaceChildren();await refreshState(version);status('Test environment ready. You received 1,000,000 free test KEY.');
});
async function write(address,abi,functionName,args,label){
 await assertWallet();
 const {request}=await publicClient.simulateContract({account,address,abi,functionName,args});
 await assertWallet();const hash=await walletClient.writeContract({...request,account,chain:baseSepolia});
 return {hash,result:await receipt(hash,label)};
}
$('approve').onclick=()=>run(async version=>{
 if(!suite||!available)throw Error('Create and verify a test environment first.');
 status('Approve exactly 750,000 test KEY for your separate test collection.');
 await write(suite.key,artifacts.key.abi,'approve',[suite.collection,TEST_PRICE],'Approve test KEY');
 await refreshState(version);status('Test KEY approval confirmed. You can now mint.');
});
$('faucet').onclick=()=>run(async version=>{
 if(!suite)throw Error('Create a test environment first.');
 await write(suite.key,artifacts.key.abi,'faucet',[account],'Receive free test KEY');
 await refreshState(version);status('Free test KEY received.');
});
$('mint').onclick=()=>run(async version=>{
 if(!suite||!available)throw Error('The test edition is unavailable.');
 const buyer=account,selectedSuite=suite;status('Confirm the test mint: 750,000 test KEY. No original island will be minted.');
 const {hash,result}=await write(suite.collection,artifacts.collection.abi,'mintWithKey',[TEST_TOKEN_ID,TEST_PRICE,keccak256(stringToHex(TEST_METADATA)),buyer],'Mint test NFT');
 if(version!==generation)throw Error('Wallet changed. Check the confirmed mint transaction in the history.');
 const events=parseEventLogs({abi:artifacts.collection.abi,logs:result.logs.filter(log=>same(log.address,selectedSuite.collection)),eventName:'MintedWithKey'});
 const paid=parseEventLogs({abi:erc20Abi,logs:result.logs.filter(log=>same(log.address,selectedSuite.key)),eventName:'Transfer'});
 if(!events.some(event=>event.args.tokenId===TEST_TOKEN_ID&&same(event.args.payer,buyer)&&same(event.args.recipient,buyer)&&event.args.price===TEST_PRICE&&same(event.args.payout,selectedSuite.treasury))||!paid.some(event=>same(event.args.from,buyer)&&same(event.args.to,selectedSuite.treasury)&&event.args.value===TEST_PRICE))throw Error('Mint receipt did not match the expected test payment. Inspect the transaction.');
 const [actualOwner,uri]=await Promise.all([
  publicClient.readContract({address:selectedSuite.collection,abi:artifacts.collection.abi,functionName:'ownerOf',args:[TEST_TOKEN_ID]}),
  publicClient.readContract({address:selectedSuite.collection,abi:artifacts.collection.abi,functionName:'tokenURI',args:[TEST_TOKEN_ID]})
 ]);
 if(!same(actualOwner,buyer)||uri!==TEST_METADATA)throw Error('Test ownership or metadata verification failed.');
 const out=$('mintResult');out.replaceChildren();
 const title=document.createElement('h3');title.textContent='Test mint confirmed ✓';
 const details=document.createElement('p');details.textContent='750,000 test KEY reached the test treasury. Test Edition 1 belongs to '+actualOwner+'. The real ISLANDS collection is unchanged.';
 out.append(title,details);link(out,'View confirmed test mint ↗',TEST_EXPLORER+'/tx/'+hash);
 await refreshState(version);status('Payment, test NFT ownership and test metadata verified on Base Sepolia.');
});
async function init(){
 try{if(await withTimeout(sdk.isInMiniApp(),2500,'Host detection timeout'))Promise.resolve().then(()=>sdk.actions.ready()).catch(()=>{});}catch{}
 try{
  const response=await fetch('/testnet/artifacts.json');if(!response.ok)throw Error();
  const data=await response.json();
  if(data.chainId!==TEST_CHAIN_ID||data.compilerVersion!=='0.8.24'||!Array.isArray(data.suite?.abi)||!/^0x[0-9a-fA-F]+$/.test(data.suite?.bytecode||''))throw Error();
  artifacts=data;status('Test contracts ready. Connect a wallet on Base Sepolia. No transaction has been sent.');
 }catch{status('The checked test contract build is not available yet. Deployment is disabled.');}
 buttons();
}
init();

export function withTimeout(work,ms,message){
 let timer;return Promise.race([Promise.resolve(work),new Promise((_,reject)=>{timer=setTimeout(()=>reject(Error(message)),ms)})]).finally(()=>clearTimeout(timer));
}
export function farcasterLaunchUrl(origin){
 const url=new URL('https://farcaster.xyz/~/mini-apps/launch');url.searchParams.set('domain',new URL(origin).hostname);return url.href;
}
export async function resolveFarcasterProvider(sdk,{timeout=5000}={}){
 // Recheck on each click: the host can respond later than the initial page load.
 const inside=await withTimeout(sdk.isInMiniApp(timeout),timeout+100,'Farcaster is taking too long to respond. Please retry.');
 if(!inside)throw Error('Open ISLANDS as a Farcaster Mini App to use your Farcaster wallet.');
 // ready() only dismisses the splash. It must not block wallet access.
 Promise.resolve().then(()=>sdk.actions.ready()).catch(()=>{});
 try{
  const provider=await withTimeout(sdk.wallet.getEthereumProvider(),timeout,'Farcaster wallet discovery timed out.');
  if(!provider)throw Error('This Farcaster host does not offer an Ethereum wallet.');
  return provider;
 }catch(error){
  // Older hosts can fail or hang in capability discovery but expose the bridge.
  if(/timed out/.test(error.message)&&sdk.wallet.ethProvider?.request)return sdk.wallet.ethProvider;
  throw error;
 }
}
export async function requestWalletAccounts(provider){
 const accounts=await provider.request({method:'eth_requestAccounts'});
 if(!/^0x[a-fA-F0-9]{40}$/.test(accounts?.[0]??''))throw Error('No wallet account was returned. Please choose an account in Farcaster.');
 return accounts;
}
export function walletError(error){
 if(error?.code===4001)return 'Wallet connection cancelled. You can try again.';
 if(error?.code===-32002)return 'A wallet request is already open. Please confirm it in Farcaster.';
 return error?.message||'Wallet connection failed. Please retry.';
}

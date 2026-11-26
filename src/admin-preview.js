// Read-only UI permission. Published artwork files are not private storage.
export const administratorWallet='0xfc5708cb64604dcf6f62de5d63a051ed577e10c1';
const same=(a,b)=>typeof a==='string'&&a.toLowerCase()===b.toLowerCase();
export function createAdminPreview({verify,origin,onChange=()=>{},now=Date.now,nonce=()=>crypto.randomUUID(),schedule=setTimeout,cancel=clearTimeout}){
 let provider=null,account=null,active=false,busy=false,expires=0,revision=0,timer=null;
 const state=()=>({eligible:same(account,administratorWallet),active:active&&now()<expires,busy});
 const notify=()=>onChange(state());
 function revoke(){revision++;active=false;busy=false;expires=0;if(timer)cancel(timer);timer=null;notify()}
 const accountsChanged=accounts=>{account=accounts?.[0]||null;revoke()};
 const disconnected=()=>{account=null;revoke()};
 const chainChanged=()=>revoke();
 function bind(next,accounts=[]){
  if(provider){provider.removeListener?.('accountsChanged',accountsChanged);provider.removeListener?.('disconnect',disconnected);provider.removeListener?.('chainChanged',chainChanged)}
  provider=next;account=accounts[0]||null;revoke();
  provider?.on?.('accountsChanged',accountsChanged);provider?.on?.('disconnect',disconnected);provider?.on?.('chainChanged',chainChanged);
 }
 async function enter(){
  if(!provider||!state().eligible||busy)throw Error('Connect the administrator wallet first.');
  revoke();busy=true;notify();const token=revision,p=provider;
  try{
   const accounts=await p.request({method:'eth_accounts'});
   if(token!==revision||!same(accounts?.[0],administratorWallet))throw Error('Wallet changed. Please reconnect.');
   const issued=now(),expiry=issued+30*60*1000;
   const message=`${new URL(origin).host} requests a read-only ISLANDS administrator preview.\n\nWallet: ${administratorWallet}\nURI: ${origin}\nPurpose: View unreleased artwork. No transaction, token approval or transfer.\nNonce: ${nonce()}\nIssued At: ${new Date(issued).toISOString()}\nExpiration Time: ${new Date(expiry).toISOString()}`;
   const hex='0x'+Array.from(new TextEncoder().encode(message),b=>b.toString(16).padStart(2,'0')).join('');
   const signature=await p.request({method:'personal_sign',params:[hex,accounts[0]]});
   if(token!==revision)throw Error('Administrator verification cancelled.');
   if(!await verify({address:administratorWallet,message,signature}))throw Error('Wallet signature could not be verified.');
   const current=await p.request({method:'eth_accounts'});
   if(token!==revision||!same(current?.[0],administratorWallet)||now()>=expiry)throw Error('Wallet changed or verification expired.');
   active=true;expires=expiry;timer=schedule(revoke,Math.max(0,expiry-now()));
  }finally{if(token===revision){busy=false;notify()}}
 }
 return {bind,enter,exit:revoke,state};
}

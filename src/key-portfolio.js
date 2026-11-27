const integer=value=>/^[0-9]+$/.test(String(value??''))?BigInt(value):null;
export function keyCount(value){const count=integer(value);return count===null?'Unavailable':count.toLocaleString('en-US');}
export function unlockLabel(value){
 if(value==null)return 'No scheduled unlock';
 const date=new Date(value);return Number.isNaN(date.getTime())?'Unavailable':date.toLocaleString('en-GB',{dateStyle:'medium',timeStyle:'short'});
}
function element(doc,tag,text,className){const node=doc.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node;}
function identity(doc,item){
 const heading=element(doc,'div',null,'key-identity');
 const name=element(doc,'h3',item.name||item.username||'Unnamed creator');
 const info=element(doc,'div');info.append(name);
 info.append(element(doc,'p',(['channel','club'].includes(item.type)?'Club':'Creator')+(item.username?' · @'+item.username:'')));
 if(typeof item.avatarUrl==='string'&&item.avatarUrl.startsWith('https://')){
  const image=element(doc,'img');image.src=item.avatarUrl;image.alt='';image.width=image.height=44;image.loading='lazy';image.referrerPolicy='no-referrer';image.onerror=()=>image.remove();heading.append(image);
 }
 heading.append(info);return heading;
}
export function renderKeyHoldings(data,out,{wallet='',onMore=null}={}){
 const doc=out.ownerDocument;out.replaceChildren();
 if(wallet)out.append(element(doc,'p','Wallet: '+wallet,'key-wallet'));
 if(!Array.isArray(data?.items))throw Error('Holdings unavailable');
 const items=data.items;
 if(!items.length){out.append(element(doc,'p','No Creator or Club Keys found for this wallet.'));return;}
 const summary=element(doc,'dl',null,'key-counts key-summary');
 const total=key=>{const values=items.map(item=>integer(item[key]));return values.some(value=>value===null)?'Unavailable':keyCount(values.reduce((sum,value)=>sum+value,0n));};
 for(const [label,value] of [['Creators / clubs shown',String(items.length)],['Available keys shown',total('liquidKeys')],['Staked keys shown',total('stakedKeys')]])summary.append(element(doc,'dt',label),element(doc,'dd',value));
 out.append(summary);
 const list=element(doc,'div',null,'key-holdings');
 for(const item of items){
  const card=element(doc,'article',null,'key-holding');card.append(identity(doc,item));
  const counts=element(doc,'dl',null,'key-counts');
  for(const [label,value] of [['Available',keyCount(item.liquidKeys)],['Staked',keyCount(item.stakedKeys)],['Unlocked stake',keyCount(item.unlockedKeys)],['Next unlock',unlockLabel(item.nextUnlockAt)]])counts.append(element(doc,'dt',label),element(doc,'dd',value));
  card.append(counts);list.append(card);
 }
 out.append(list);
 const note=element(doc,'small','Indexed BaseFriend balances may update with a delay. Unlocked stake is included in staked keys.');out.append(note);
 if(data.nextCursor&&onMore){const more=element(doc,'button','Load more keys','outline');more.type='button';more.onclick=()=>onMore(data.nextCursor);out.append(more);}
}
export function renderCreatorMarkets(data,out){
 out.replaceChildren();if(!Array.isArray(data?.items))throw Error('Creator search unavailable');
 if(!data.items.length){out.append(element(out.ownerDocument,'p','No creators found.'));return;}
 for(const item of data.items){const card=element(out.ownerDocument,'article',null,'key-holding');card.append(identity(out.ownerDocument,item));out.append(card);}
}
export function createKeyPortfolio(out,{fetchPage,onBusy=()=>{}}){
 let generation=0,items=[],wallet='',busy=false;
 const show=data=>renderKeyHoldings({...data,items},out,{wallet,onMore:cursor=>loadMore(cursor)});
 async function request(cursor,version){
  busy=true;onBusy(true);
  try{
   const data=await fetchPage(wallet,cursor);
   if(version!==generation)return;
   if(!Array.isArray(data?.items))throw Error('Holdings unavailable');
   // A page may repeat a market; show each holding once.
   items=[...new Map([...items,...data.items].map(item=>[item.id??item.tokenId,item])).values()];
   show(data);
  }catch{
   if(version!==generation)return;
   if(!cursor)out.textContent='Could not load your keys. Please try again.';
   else{show({nextCursor:cursor});out.append(element(out.ownerDocument,'p','Could not load more keys. Please retry.'));}
  }finally{if(version===generation){busy=false;onBusy(false);}}
 }
 async function loadMore(cursor){if(busy)return;await request(cursor,generation);}
 return {
  async load(address){
   if(!/^0x[0-9a-fA-F]{40}$/.test(address)){out.textContent='Enter a valid Base wallet address.';return;}
   const version=++generation;wallet=address;items=[];out.textContent='Loading your keys…';await request(null,version);
  },
  clear(){generation++;items=[];wallet='';busy=false;onBusy(false);out.replaceChildren();}
 };
}

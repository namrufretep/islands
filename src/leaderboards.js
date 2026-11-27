import {hasVerifiedMint} from './gallery-inventory.js';
const addressPattern=/^0x[0-9a-fA-F]{40}$/;
const editionPattern=/^\d{6}-[NS]$/;
const SCALE=10n**36n;
function inventory(editions){return [...new Map(editions.filter(e=>hasVerifiedMint(e)&&editionPattern.test(e.id)).map(e=>[e.id,e])).values()];}
function islandId(edition){return edition.id.slice(0,6);}
function ranked(rows,score){let previous=null,rank=0;return rows.map((row,index)=>{const value=score(row);if(value!==previous)rank=index+1;previous=value;return {...row,rank};});}
export function collectorLeaderboard(editions){
 const wallets=new Map();
 for(const edition of inventory(editions)){
  if(!addressPattern.test(edition.chain.ownedBy||''))continue;
  const address=edition.chain.ownedBy.toLowerCase();
  if(!wallets.has(address))wallets.set(address,{address,islandIds:new Set(),editions:0});
  const row=wallets.get(address);row.islandIds.add(islandId(edition));row.editions++;
 }
 const rows=[...wallets.values()].map(({islandIds,...row})=>({...row,islands:islandIds.size}));
 rows.sort((a,b)=>b.islands-a.islands||b.editions-a.editions||a.address.localeCompare(b.address));
 return ranked(rows,row=>row.islands);
}
// Input must come from a receipt-verified CHEERS index. Never count clicks,
// pending transfers, or generic token transfers as confirmed island tips.
export function islandCheersLeaderboard(editions,events,{sort='amount'}={}){
 const known=new Map(inventory(editions).map(e=>[e.id,e]));const seen=new Set(),islands=new Map();
 for(const event of events){
  if(event.verified!==true||event.status!=='confirmed'||event.chainId!==8453||!/^0x[0-9a-fA-F]{64}$/.test(event.transactionHash||'')||!Number.isSafeInteger(event.logIndex)||event.logIndex<0)continue;
  const edition=known.get(event.editionId);if(!edition)continue;
  if(!/^\d+$/.test(String(event.amountAtoms??''))||!Number.isInteger(event.decimals)||event.decimals<0||event.decimals>36)continue;
  const amount=BigInt(event.amountAtoms);if(amount<=0n)continue;
  const key=event.chainId+':'+event.transactionHash.toLowerCase()+':'+event.logIndex;if(seen.has(key))continue;seen.add(key);
  const id=islandId(edition);if(!islands.has(id))islands.set(id,{islandId:id,name:edition.name,editionId:edition.id,amountUnits:0n,tips:0});
  const row=islands.get(id);row.amountUnits+=amount*10n**BigInt(36-event.decimals);row.tips++;
 }
 const rows=[...islands.values()];const compareAmount=(a,b)=>a.amountUnits===b.amountUnits?0:a.amountUnits>b.amountUnits?-1:1;
 rows.sort((a,b)=>(sort==='tips'?b.tips-a.tips||compareAmount(a,b):compareAmount(a,b)||b.tips-a.tips)||a.name.localeCompare(b.name)||a.islandId.localeCompare(b.islandId));
 return ranked(rows,row=>sort==='tips'?row.tips:row.amountUnits.toString()).map(row=>({...row,amountUnits:row.amountUnits.toString()}));
}
export function formatCheers(value){const units=BigInt(value);const whole=(units/SCALE).toLocaleString('en-US'),fraction=(units%SCALE).toString().padStart(36,'0').replace(/0+$/,'');return whole+(fraction?'.'+fraction:'');}
function confirmedTrades(editions,events){
 const known=new Map(inventory(editions).map(edition=>[edition.id,edition])),seen=new Set(),trades=[];
 for(const event of events){
  if(event.verified!==true||event.status!=='confirmed'||event.chainId!==8453||!['sale','swap'].includes(event.kind)||!/^0x[0-9a-fA-F]{64}$/.test(event.transactionHash||'')||!Number.isSafeInteger(event.logIndex)||event.logIndex<0||!Array.isArray(event.editionIds)||!event.editionIds.length)continue;
  if(event.editionIds.some(id=>!known.has(id)))continue;
  const key=event.chainId+':'+event.transactionHash.toLowerCase()+':'+event.logIndex;if(seen.has(key))continue;seen.add(key);
  trades.push([...new Map(event.editionIds.map(id=>{const edition=known.get(id);return [islandId(edition),edition];})).values()]);
 }
 return trades;
}
export function islandTradeLeaderboard(editions,events){
 const islands=new Map();
 for(const trade of confirmedTrades(editions,events))for(const edition of trade){
  const id=islandId(edition);if(!islands.has(id))islands.set(id,{islandId:id,name:edition.name,editionId:edition.id,trades:0});islands.get(id).trades++;
 }
 return ranked([...islands.values()].sort((a,b)=>b.trades-a.trades||a.name.localeCompare(b.name)||a.islandId.localeCompare(b.islandId)),row=>row.trades);
}
export function buildLeaderboards(editions,events=[],trades=[]){
 const minted=inventory(editions),collectors=collectorLeaderboard(minted),byAmount=islandCheersLeaderboard(minted,events),byTrades=islandTradeLeaderboard(minted,trades);
 return {collectors,byAmount,byTrades,mintedIslands:new Set(minted.map(islandId)).size,mintedEditions:minted.length,recordedTips:byAmount.reduce((n,row)=>n+row.tips,0),recordedCheersUnits:byAmount.reduce((n,row)=>n+BigInt(row.amountUnits),0n).toString(),recordedTrades:confirmedTrades(minted,trades).length};
}

import {formatCheers} from './leaderboards.js';
function el(doc,tag,text,className){const node=doc.createElement(tag);if(text!=null)node.textContent=text;if(className)node.className=className;return node;}
export function renderLeaderboards(data,out,{mode='collectors',onIsland=()=>{}}={}){
 const doc=out.ownerDocument;out.replaceChildren();
 const stats=el(doc,'dl',null,'leaderboard-stats');
 for(const [label,value] of [['Minted islands',data.mintedIslands],['Collectors',data.collectors.length],['Recorded CHEERS',formatCheers(data.recordedCheersUnits)],['Completed trades',data.recordedTrades]]){
  const cell=el(doc,'div');cell.append(el(doc,'dt',label),el(doc,'dd',String(value)));stats.append(cell);
 }
 out.append(stats);
 const config={collectors:{title:'Top collectors',rows:data.collectors,columns:['Rank','Collector','Islands','Editions'],empty:'No minted islands yet. Collectors will appear after ownership is confirmed.'},cheers:{title:'Islands with the most CHEERS',rows:data.byAmount,columns:['Rank','Island','CHEERS received'],empty:'No confirmed island CHEERS yet. CHEERS payments are not active.'},trades:{title:'Most traded islands',rows:data.byTrades,columns:['Rank','Island','Completed trades'],empty:'No confirmed trades yet. Trading is not active.'}}[mode];
 out.append(el(doc,'h2',config.title));
 if(!config.rows.length){out.append(el(doc,'p',config.empty,'leaderboard-empty'));return;}
 const wrapper=el(doc,'div',null,'leaderboard-scroll'),table=el(doc,'table',null,'leaderboard-table');table.append(el(doc,'caption',config.title));
 const head=el(doc,'thead'),header=el(doc,'tr');for(const name of config.columns){const th=el(doc,'th',name);th.scope='col';header.append(th);}head.append(header);table.append(head);
 const body=el(doc,'tbody');
 for(const row of config.rows){
  const tr=el(doc,'tr');tr.append(el(doc,'td',String(row.rank)));
  const identity=el(doc,'td');
  if(mode==='collectors'){const wallet=el(doc,'span',row.address.slice(0,6)+'…'+row.address.slice(-4));wallet.title=row.address;identity.append(wallet);tr.append(identity,el(doc,'td',String(row.islands)),el(doc,'td',String(row.editions)));}
  else{
   const button=el(doc,'button',row.name,'leaderboard-island');button.type='button';button.onclick=()=>onIsland(row.editionId);identity.append(button);tr.append(identity,el(doc,'td',mode==='cheers'?formatCheers(row.amountUnits):String(row.trades)));
  }
  body.append(tr);
 }
 table.append(body);wrapper.append(table);out.append(wrapper);
}

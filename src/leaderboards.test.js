import test from 'node:test';
import assert from 'node:assert/strict';
import {buildLeaderboards,formatCheers,islandCheersLeaderboard} from './leaderboards.js';
const a='0x'+'a'.repeat(40),b='0x'+'b'.repeat(40);
const edition=(id,owner=a,name='Island '+id.slice(0,6))=>({id,name,chain:{verified:true,minted:true,ownedBy:owner,mintedBy:b}});
const tip=(editionId,amountAtoms,logIndex=0,extra={})=>({verified:true,status:'confirmed',chainId:8453,transactionHash:'0x'+'1'.repeat(64),logIndex,editionId,amountAtoms,decimals:0,...extra});
test('collector rank uses unique islands and current owners, not minters or preview artwork',()=>{
 const data=buildLeaderboards([edition('000001-N'),edition('000001-S'),edition('000002-N'),edition('000003-N',b),{id:'000004-N',chain:{verified:false,minted:true,ownedBy:b}}]);
 assert.equal(data.collectors[0].address,a);assert.equal(data.collectors[0].islands,2);assert.equal(data.collectors[0].editions,3);
 assert.equal(data.collectors[1].islands,1);assert.equal(data.mintedIslands,3);
 const transfer=buildLeaderboards([edition('000001-N'),edition('000001-N',b)]);assert.equal(transfer.collectors.length,1);assert.equal(transfer.collectors[0].address,b);
});
test('CHEERS totals and tip frequency rank differently and merge both orientations',()=>{
 const editions=[edition('000001-N'),edition('000001-S'),edition('000002-N')];
 const data=buildLeaderboards(editions,[tip('000001-N','750',0),tip('000002-N','250',1),tip('000002-N','250',2),tip('000001-S','250',3)]);
 assert.equal(data.byAmount[0].islandId,'000001');assert.equal(formatCheers(data.byAmount[0].amountUnits),'1,000');assert.equal(data.byAmount[0].tips,2);
 assert.equal(data.recordedTips,4);assert.equal(formatCheers(data.recordedCheersUnits),'1,500');
 const frequency=buildLeaderboards(editions,[tip('000001-N','1000'),tip('000002-N','1',1),tip('000002-N','1',2)]);
 assert.equal(frequency.byAmount[0].islandId,'000001');assert.equal(islandCheersLeaderboard(editions,[tip('000001-N','1000'),tip('000002-N','1',1),tip('000002-N','1',2)],{sort:'tips'})[0].islandId,'000002');
});
test('duplicates, pending tips, wrong chains and unminted editions never inflate rankings',()=>{
 const valid=tip('000001-N','250');const data=buildLeaderboards([edition('000001-N')],[valid,valid,{...valid,status:'pending',logIndex:1},{...valid,verified:false,logIndex:2},{...valid,chainId:1,logIndex:3},{...valid,editionId:'000002-N',logIndex:4},{...valid,amountAtoms:'0',logIndex:5},{...valid,transactionHash:'invalid',logIndex:6}]);
 assert.equal(data.recordedTips,1);assert.equal(formatCheers(data.recordedCheersUnits),'250');
});
test('decimal conversion preserves exact amounts and ties share a rank',()=>{
 const data=buildLeaderboards([edition('000001-N'),edition('000002-N',b)],[tip('000001-N','250000000000000000000',0,{decimals:18}),tip('000002-N','250',1)]);
 assert.deepEqual(data.collectors.map(row=>row.rank),[1,1]);assert.deepEqual(data.byAmount.map(row=>row.rank),[1,1]);assert.equal(formatCheers(data.recordedCheersUnits),'500');
 assert.equal(formatCheers('1'),'0.000000000000000000000000000000000001');
});
test('unreleased artwork has no owners or CHEERS rankings',()=>{
 const data=buildLeaderboards([{id:'000001-N',chain:{verified:true,minted:false}}],[tip('000001-N','999')]);
 assert.equal(data.mintedIslands,0);assert.deepEqual(data.collectors,[]);assert.deepEqual(data.byAmount,[]);assert.equal(data.recordedTips,0);
});

test('trade rankings count executed sales/swaps, never minting, gifts, failed or duplicate events',()=>{
 const editions=[edition('000001-N'),edition('000001-S'),edition('000002-N')];
 const sale={verified:true,status:'confirmed',chainId:8453,transactionHash:'0x'+'2'.repeat(64),logIndex:0,kind:'sale',editionIds:['000001-N']};
 const swap={...sale,logIndex:1,kind:'swap',editionIds:['000001-S','000002-N']};
 const data=buildLeaderboards(editions,[],[sale,sale,swap,{...sale,logIndex:2,kind:'transfer'},{...sale,logIndex:3,kind:'mint'},{...sale,logIndex:4,status:'failed'},{...sale,logIndex:5,verified:false}]);
 assert.equal(data.recordedTrades,2);assert.equal(data.byTrades[0].islandId,'000001');assert.equal(data.byTrades[0].trades,2);assert.equal(data.byTrades[1].trades,1);
 const sameIsland=buildLeaderboards(editions,[],[{...swap,editionIds:['000001-N','000001-S']}]);assert.equal(sameIsland.byTrades[0].trades,1);
});

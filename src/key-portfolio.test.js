import test from 'node:test';
import assert from 'node:assert/strict';
import {keyCount,unlockLabel,renderKeyHoldings,createKeyPortfolio} from './key-portfolio.js';
function fixture(){
 const doc={createElement:tag=>({tag,ownerDocument:doc,children:[],textContent:'',append(...items){this.children.push(...items)},replaceChildren(...items){this.children=items;this.textContent='';}})};
 const out=doc.createElement('div');return {out,text:()=>flatten(out)};
}
function flatten(node){return [node.textContent,...node.children.map(flatten)].join(' ');}
const holding=(id,name='Creator')=>({id,name,username:'creator',liquidKeys:'2',stakedKeys:'1',unlockedKeys:'1',nextUnlockAt:null});
test('counts stay exact; absent balances are not invented as zero',()=>{
 assert.equal(keyCount('900719925474099312345'),'900,719,925,474,099,312,345');
 assert.equal(keyCount('0'),'0');for(const v of [null,undefined,'abc','-1','1.5'])assert.equal(keyCount(v),'Unavailable');
 assert.equal(unlockLabel(null),'No scheduled unlock');assert.equal(unlockLabel('bad'),'Unavailable');
});
test('holdings show readable names and balances without raw prices or code',()=>{
 const f=fixture();renderKeyHoldings({items:[{...holding('one','<script>example</script>'),indicativeBuyPriceAtoms:'99999999999999999999'}]},f.out);
 const text=f.text();assert.ok(text.includes('<script>example</script>')); // Treated as textContent, never HTML.
 for(const label of ['Available','Staked','Unlocked stake','Next unlock'])assert.ok(text.includes(label));
 assert.ok(!text.includes('indicativeBuyPriceAtoms'));assert.ok(!text.includes('99999999999999999999'));
 assert.equal(f.out.children.find(x=>x.tag==='dl').children[5].textContent,'1');
});
test('load-more retains prior pages and deduplicates overlapping creators',async()=>{
 const f=fixture(),calls=[];
 const view=createKeyPortfolio(f.out,{fetchPage:async(wallet,cursor)=>{calls.push(cursor);return cursor?{items:[holding('one'),holding('two','Second')],nextCursor:null}:{items:[holding('one')],nextCursor:'next'};}});
 await view.load('0x'+'1'.repeat(40));
 const more=f.out.children.find(x=>x.tag==='button');await more.onclick();
 assert.deepEqual(calls,[null,'next']);assert.equal(f.out.children.find(x=>x.className==='key-holdings').children.length,2);
 assert.equal(f.out.children.some(x=>x.tag==='button'),false);assert.ok(f.text().includes('Second'));
});
test('changing wallet ignores an earlier pending portfolio response',async()=>{
 const f=fixture();let complete;
 const view=createKeyPortfolio(f.out,{fetchPage:wallet=>wallet.endsWith('1')?new Promise(resolve=>complete=resolve):Promise.resolve({items:[holding('new','New wallet')],nextCursor:null})});
 const old=view.load('0x'+'1'.repeat(40));await view.load('0x'+'2'.repeat(40));complete({items:[holding('old','Wrong wallet')],nextCursor:null});await old;
 assert.ok(f.text().includes('New wallet'));assert.ok(!f.text().includes('Wrong wallet'));
});
test('errors and empty portfolios have a useful message',async()=>{
 const f=fixture();renderKeyHoldings({items:[]},f.out);assert.match(f.text(),/No Creator or Club Keys/);
 const view=createKeyPortfolio(f.out,{fetchPage:async()=>{throw Error('Network')}});await view.load('0x'+'1'.repeat(40));assert.match(f.out.textContent,/Could not load your keys/);
});

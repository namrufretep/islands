import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {islandActions,mintEntryUrl} from './island-acquisition.js';
const origin='https://islands-kappa.vercel.app';
test('island actions distinguish reservation, primary acquisition, resale and unknown issuance',()=>{
 assert.deepEqual(islandActions({artwork:'Not existing',mint:'Not minted'}),['reserve']);
 assert.deepEqual(islandActions({artwork:'Exists',mint:'Not minted'}),['buy','luck']);
 assert.deepEqual(islandActions({artwork:'Exists',mint:'Minted'}),['offer']);
 assert.deepEqual(islandActions({artwork:'Exists',mint:'Not verified'}),[]);
});
test('direct mint routes retain exact N/S edition; luck clears the direct selection',()=>{
 for(const id of ['000076-N','000076-S']){
  const url=new URL(mintEntryUrl('direct',id,origin));assert.equal(url.origin,origin);
  assert.equal(url.searchParams.get('mint'),'direct');assert.equal(url.searchParams.get('destination'),id);
 }
 const luck=new URL(mintEntryUrl('blind','000076-N',origin));
 assert.equal(luck.searchParams.get('mint'),'blind');assert.equal(luck.searchParams.has('destination'),false);
 assert.throws(()=>mintEntryUrl('direct','../bad',origin));assert.throws(()=>mintEntryUrl('unknown',null,origin));
});
test('detail and gallery actions route exact editions without requesting payment',()=>{
 const source=readFileSync(new URL('./main.js',import.meta.url),'utf8');
 const helper=source.slice(source.indexOf('function acquisitionButtons('),source.indexOf('function openOffer('));
 const document={createElement:tag=>({tag,children:[],append(...items){this.children.push(...items);}})};
 const calls=[];
 const render=new Function('document','islandActions','openMint','openOffer',helper+';return acquisitionButtons;')(document,islandActions,(...args)=>calls.push(args),edition=>calls.push(['offer',edition.id]));
 for(const suffix of ['N','S']){
  const edition={id:'000076-'+suffix};
  const buttons=render({artwork:'Exists',mint:'Not minted'},edition).children;
  assert.deepEqual(buttons.map(b=>b.textContent),['Buy · 750,000 $KEY','Try your luck →']);
  buttons[0].onclick();assert.deepEqual(calls.pop(),['direct',edition.id]);
  buttons[1].onclick();assert.deepEqual(calls.pop(),['blind']);
  const offer=render({artwork:'Exists',mint:'Minted'},edition).children[0];
  assert.equal(offer.textContent,'Make an offer');offer.onclick();assert.deepEqual(calls.pop(),['offer',edition.id]);
 }
 const reservation=render({artwork:'Not existing',mint:'Not minted'},null).children.find(item=>item.tag==='button');
 assert.equal(reservation.disabled,true);
});

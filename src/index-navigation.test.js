import test from 'node:test';
import assert from 'node:assert/strict';
import {indexLetters,islandInitial,selectIndexRows,revealIndexArtwork} from './index-navigation.js';
import {editionStatus} from './edition-status.js';
import {editionUrl} from './sharing.js';

test('alphabet groups accents and leading island-name punctuation with their letters',()=>{
 for(const name of ["'Ā’iqah",'ʻAio','’Abd al Kūrī'])assert.equal(islandInitial(name),'A');
 assert.equal(islandInitial('Île de la Cité'),'I');assert.equal(islandInitial('Øksnes'),'O');
 assert.equal(islandInitial('小島'),'#');assert.equal(islandInitial('123 Island'),'#');
 assert.equal(indexLetters.length,28);
});
test('letter, search and artwork availability combine without losing other initials',()=>{
 const rows=[["’Abd al Kūrī",'Yemen','Arabian Sea'],['Annobón','Equatorial Guinea','Gulf of Guinea'],['Buvuma','Uganda','Lake Victoria'],['小島','Japan','Pacific']];
 const exists=row=>row[0]==='Annobón'||row[0]==='Buvuma';
 assert.equal(selectIndexRows(rows,{letter:'A'},exists).length,2);
 assert.deepEqual(selectIndexRows(rows,{letter:'A',status:'Exists'},exists).map(r=>r[0]),['Annobón']);
 assert.deepEqual(selectIndexRows(rows,{letter:'A',query:'arabian',status:'Not existing'},exists).map(r=>r[0]),['’Abd al Kūrī']);
 assert.deepEqual(selectIndexRows(rows,{letter:'#'},exists).map(r=>r[0]),['小島']);
 assert.equal(selectIndexRows(rows,{letter:'All'},exists).length,4);
});
test('full alphabetical order ignores leading punctuation as well as accents',()=>{
 const rows=[['ʻB Island'],['Zebra'],['Alpha'],['’Á Island']];
 assert.deepEqual(selectIndexRows(rows,{},()=>false).map(r=>r[0]),['’Á Island','Alpha','ʻB Island','Zebra']);
});
test('unknown onchain state cannot reveal an index artwork',()=>{
 const preview=editionStatus({artworkExists:true,collectionReleased:false});
 const unknown=editionStatus({artworkExists:true,collectionReleased:true});
 for(const state of [preview,unknown])assert.equal(revealIndexArtwork({fromIndex:true,mint:state.mint}),false);
 const minted=editionStatus({artworkExists:true,collectionReleased:true,chain:{verified:true,minted:true}});
 assert.equal(revealIndexArtwork({fromIndex:true,mint:minted.mint}),true);
 assert.equal(revealIndexArtwork({fromIndex:false,mint:preview.mint}),true);
});
test('index discovery context survives a reload of an edition link',()=>{
 const url=new URL(editionUrl('000057-S','https://islands-kappa.vercel.app',{fromIndex:true}));
 assert.equal(url.searchParams.get('view'),'index');assert.equal(url.searchParams.get('edition'),'000057-S');
 assert.equal(new URL(editionUrl('000057-S',url.origin)).searchParams.has('view'),false);
});
test('existing artwork stays first in A–Z, Z–A, country and initial filters',()=>{
 const rows=[['Alpha','Zambia'],['Zebra','Austria'],['Zulu','Zambia'],['Amber','Austria'],['Aster','Brazil']];
 const exists=r=>['Alpha','Zulu','Amber'].includes(r[0]);
 const names=options=>selectIndexRows(rows,options,exists).map(r=>r[0]);
 assert.deepEqual(names({sort:0}),['Alpha','Amber','Zulu','Aster','Zebra']);
 assert.deepEqual(names({sort:3}),['Zulu','Amber','Alpha','Zebra','Aster']);
 assert.deepEqual(names({sort:1}),['Amber','Alpha','Zulu','Zebra','Aster']);
 assert.deepEqual(names({sort:4}),['Zulu','Alpha','Amber','Aster','Zebra']);
 assert.deepEqual(names({sort:3,letter:'A'}),['Amber','Alpha','Aster']);
 assert.deepEqual(names({sort:0,status:'Not existing'}),['Aster','Zebra']);
});
test('verified administrator session can preview concealed index artwork',()=>{
 assert.equal(revealIndexArtwork({fromIndex:true,mint:'Not minted',administrator:true}),true);
 assert.equal(revealIndexArtwork({fromIndex:true,mint:'Not minted',administrator:false}),false);
});

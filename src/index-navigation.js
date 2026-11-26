export const indexLetters=['All',...'ABCDEFGHIJKLMNOPQRSTUVWXYZ','#'];
const collator=new Intl.Collator('en',{sensitivity:'base',numeric:true,ignorePunctuation:true});
const fold=value=>String(value||'').normalize('NFKD').replace(/\p{M}/gu,'').replace(/[Ææ]/g,'ae').replace(/[Œœ]/g,'oe').replace(/[Øø]/g,'o').replace(/[Łł]/g,'l').replace(/[ĐđÐð]/g,'d').replace(/[Þþ]/g,'th').replace(/ß/g,'ss').toLowerCase();
const nameKey=name=>fold(name).replace(/^[\p{P}\p{Z}\p{S}\sʻʼʿʾ]+/u,'');

export function islandInitial(name){
 const key=nameKey(name);
 return /^[a-z]/.test(key)?key[0].toUpperCase():'#';
}

export function selectIndexRows(rows,{query='',letter='All',status='All',sort=0},hasArtwork){
 const search=fold(query.trim()),column=({0:0,1:1,2:2,3:0,4:1,5:2})[sort]??0,direction=sort>=3?-1:1;
 const matches=rows.filter(row=>
  (letter==='All'||islandInitial(row[0])===letter)&&
  (!search||fold(row.slice(0,3).join(' ')).includes(search))&&
  (status==='All'||status===(hasArtwork(row)?'Exists':'Not existing'))
 );
 const names=new Map(matches.map(row=>[row,nameKey(row[0])]));
 const exists=new Map(matches.map(row=>[row,Boolean(hasArtwork(row))]));
 return matches.sort((a,b)=>Number(exists.get(b))-Number(exists.get(a))||direction*(collator.compare(column===0?names.get(a):a[column],column===0?names.get(b):b[column])||collator.compare(names.get(a),names.get(b))));
}

// Index discovery conceals unminted or unverified art; gallery previews are separate.
export function revealIndexArtwork({fromIndex,mint,administrator=false}){
 return administrator||!fromIndex||mint==='Minted';
}

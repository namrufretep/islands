// Artwork existence and confirmed NFT issuance lead to different acquisition paths.
export function islandActions({artwork, mint}) {
 if(mint==='Minted')return ['offer'];
 if(artwork==='Not existing')return ['reserve'];
 if(artwork==='Exists'&&mint==='Not minted')return ['buy','luck'];
 return [];
}
export function mintEntryUrl(mode,editionId,origin) {
 if(!['blind','regional','direct'].includes(mode))throw Error('Invalid mint mode');
 if(mode==='direct'&&!/^\d{6}-[NS]$/.test(editionId||''))throw Error('Invalid artwork edition');
 const url=new URL('/',origin);url.searchParams.set('mint',mode);
 if(mode==='direct')url.searchParams.set('destination',editionId);
 return url.href;
}

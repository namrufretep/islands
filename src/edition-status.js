const walletPattern=/^0x[0-9a-fA-F]{40}$/;
const shortWallet=value=>walletPattern.test(value||'')?value.slice(0,6)+'…'+value.slice(-4):'Not verified';

// Artwork availability is independent of NFT issuance and current ownership.
// A released collection with no confirmed chain response must remain unknown.
export function editionStatus({artworkExists,collectionReleased,chain=null}){
 const confirmed=chain?.verified===true&&typeof chain.minted==='boolean';
 const minted=confirmed?chain.minted:collectionReleased===false?false:null;
 const wallet=key=>minted===false?'—':confirmed&&minted?shortWallet(chain[key]):'Not verified';
 return {
  artwork:artworkExists?'Exists':'Not existing',
  mint:minted===true?'Minted':minted===false?'Not minted':'Not verified',
  mintedBy:wallet('mintedBy'),ownedBy:wallet('ownedBy'),
  mintedByAddress:confirmed&&minted&&walletPattern.test(chain.mintedBy||'')?chain.mintedBy:null,
  ownedByAddress:confirmed&&minted&&walletPattern.test(chain.ownedBy||'')?chain.ownedBy:null
 };
}

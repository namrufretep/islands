// Public collection membership requires confirmed issuance, not a preview/status label.
export const hasVerifiedMint=edition=>edition?.chain?.verified===true&&edition.chain.minted===true;
export function galleryInventory(published,previews,{administrator=false}={}){
 const editions=administrator?[...previews,...published]:published.filter(hasVerifiedMint);
 return [...new Map(editions.map(edition=>[edition.id,edition])).values()];
}

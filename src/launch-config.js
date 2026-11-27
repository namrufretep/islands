import {mintPrice} from './pricing.js';

export const MAINNET_CHAIN_ID=8453;
export const MAINNET_RPC='https://mainnet.base.org';
export const KEY_ADDRESS='0xb0ca1e094a1779018b194ac6151ece8d6f05db07';
export const CREATOR_ADDRESS='0xfc5708cb64604dcf6f62de5d63a051ed577e10c1';
export const DIRECT_KEY_PRICE=750000n*10n**18n;
export const LAUNCH_ISLAND_TARGET=500;
export const STAKE_TIERS=[0,1,5,15,30,50];
export const mintQuoteFields=[
 ['payer','address'],['recipient','address'],['tokenId','uint256'],['basePrice','uint256'],
 ['stakedKeys','uint256'],['stakeBlock','uint256'],['issuedAt','uint256'],['deadline','uint256'],
 ['nonce','uint256'],['verifierVersion','uint256'],['metadataHash','bytes32']
].map(([name,type])=>({name,type}));

export function canonicalTokenId(artworkId){
 const match=/^(\d{6})-([NS])$/.exec(artworkId);
 if(!match||Number(match[1])<1)throw Error('Invalid canonical artwork ID');
 return Number(match[1])*2-(match[2]==='N'?1:0);
}
export function directPriceForStake(verifiedCount){return mintPrice(DIRECT_KEY_PRICE,verifiedCount);}
// Constructing this data does not prove eligibility. Only the configured verifier may sign it.
export function stakingQuoteTypedData(collection,message){
 if(!/^0x[0-9a-fA-F]{40}$/.test(collection))throw Error('Invalid collection address');
 return {domain:{name:'ISLANDS Mint',version:'1',chainId:MAINNET_CHAIN_ID,verifyingContract:collection},types:{MintQuote:mintQuoteFields},primaryType:'MintQuote',message};
}

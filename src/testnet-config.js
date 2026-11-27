export const TEST_CHAIN_ID=84532;
export const TEST_CHAIN_HEX='0x14a34';
export const TEST_PRICE=750000n*10n**18n;
export const TEST_TOKEN_ID=1n;
export const TEST_METADATA='https://islands-kappa.vercel.app/testnet/edition.json';
export const TEST_RPC='https://sepolia.base.org';
export const TEST_EXPLORER='https://sepolia.basescan.org';
export function assertTestChain(chainId){
 let value;try{value=BigInt(chainId);}catch{throw Error('Cannot verify wallet network.');}
 if(value!==BigInt(TEST_CHAIN_ID))throw Error('Test actions require Base Sepolia (84532). No transaction was sent.');
}
export function deploymentMatches(transaction,receipt,bytecode){
 return receipt?.status==='success'&&/^0x[0-9a-fA-F]{40}$/.test(receipt.contractAddress||'')&&
  transaction?.to===null&&typeof transaction.input==='string'&&transaction.input.toLowerCase()===bytecode.toLowerCase();
}
export function validTransactionHash(value){return /^0x[0-9a-fA-F]{64}$/.test(value||'');}

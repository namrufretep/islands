// Read-only checks. No signing key, wallet signing or send-transaction method is used.
import {readFileSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {MAINNET_CHAIN_ID,MAINNET_RPC,KEY_ADDRESS,CREATOR_ADDRESS} from '../src/launch-config.js';
const root=fileURLToPath(new URL('../',import.meta.url));
const artifact=JSON.parse(readFileSync(root+'public/launch/artifacts.json'));
for(const [name,hash] of Object.entries(artifact.sourceSha256))if(createHash('sha256').update(readFileSync(root+'contracts/'+name)).digest('hex')!==hash)throw Error('Stale compiled artifact: '+name);
async function rpc(method,params=[]){
 const response=await fetch(MAINNET_RPC,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params}),signal:AbortSignal.timeout(30000)});
 if(!response.ok)throw Error('Base RPC HTTP '+response.status);
 const result=await response.json();if(result.error)throw Error(JSON.stringify(result.error));return result.result;
}
const chain=Number(BigInt(await rpc('eth_chainId')));if(chain!==MAINNET_CHAIN_ID)throw Error('Wrong RPC chain');
const block=await rpc('eth_blockNumber');
const [code,decimals,symbol]=await Promise.all([
 rpc('eth_getCode',[KEY_ADDRESS,block]),rpc('eth_call',[{to:KEY_ADDRESS,data:'0x313ce567'},block]),rpc('eth_call',[{to:KEY_ADDRESS,data:'0x95d89b41'},block])
]);
if(code==='0x'||Number(BigInt(decimals))!==18)throw Error('KEY contract or decimals mismatch');
// ABI dynamic string response, not a presumed ticker from a token list.
const payload=symbol.slice(2),offset=Number(BigInt('0x'+payload.slice(0,64)))*2;
const length=Number(BigInt('0x'+payload.slice(offset,offset+64)));
if(length>100)throw Error('Invalid token symbol');
const actualSymbol=Buffer.from(payload.slice(offset+64,offset+64+length*2),'hex').toString('utf8');
// This deployed token has a trailing space in its symbol. Preserve the exact RPC value in the report.
if(actualSymbol.trim()!=='KEY')throw Error('Unexpected token symbol: '+actualSymbol);
const tx={from:CREATOR_ADDRESS,data:artifact.bytecode,value:'0x0'};
const gas=await rpc('eth_estimateGas',[tx]);
const simulatedRuntime=await rpc('eth_call',[tx,block]);
if(simulatedRuntime.length<4)throw Error('Empty deployment simulation');
const report={checked_at:new Date().toISOString(),chain_id:chain,block_number:Number(BigInt(block)),key_address:KEY_ADDRESS,key_symbol:actualSymbol,key_decimals:18,key_code_sha256:createHash('sha256').update(Buffer.from(code.slice(2),'hex')).digest('hex'),deployment_simulation:'success',deployment_gas_units:BigInt(gas).toString(),transaction_sent:false,collection_deployed:false,public_mint_open:false,limitations:['RPC simulation is not an audit or wallet-security classification','KEY token implementation, admin controls and transfer behavior require separate review','Staking verification service and blind/regional selection remain unconnected','No real KEY payment or OpenSea indexing tested']};
writeFileSync(root+'public/launch/mainnet-check.json',JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));

import fs from 'node:fs';
const from='0xfc5708cb64604dcf6f62de5d63a051ed577e10c1';
const artifact=JSON.parse(fs.readFileSync('public/testnet/artifacts.json','utf8'));
async function rpc(method,params=[]){const r=await fetch('https://sepolia.base.org',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params}),signal:AbortSignal.timeout(30000)});const j=await r.json();if(j.error)throw Error(JSON.stringify(j.error));return j.result;}
const chain=await rpc('eth_chainId');if(BigInt(chain)!==84532n)throw Error('Wrong chain');
for(const method of ['eth_getBalance','eth_getTransactionCount','eth_getCode'])console.log('DIAG',method,await rpc(method,[from,'latest']));
const tx={from,data:artifact.suite.bytecode,value:'0x0'};
for(const method of ['eth_estimateGas','eth_call']){try{const result=await rpc(method,[tx,'latest']);console.log('DIAG',method,result);}catch(e){console.log('DIAG',method,'ERROR',e.message);process.exitCode=1;}}
for(const method of ['eth_gasPrice','eth_maxPriorityFeePerGas']){try{console.log('DIAG',method,await rpc(method));}catch(e){console.log('DIAG',method,'ERROR',e.message);}}

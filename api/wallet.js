export default async function handler(req,res){
if(req.method!=='GET')return res.status(405).end();
const wallet=req.query.wallet;if(typeof wallet!=='string'||!/^0x[a-fA-F0-9]{40}$/.test(wallet))return res.status(400).json({error:'Invalid wallet'});
const q=new URLSearchParams({wallet});if(typeof req.query.cursor==='string')q.set('cursor',req.query.cursor.slice(0,2048));
try{const key=process.env.BASEFRIEND_APP_API_KEY;const r=await fetch('https://basefriend.tech/api/public/basefriend/v1/wallet?'+q,{headers:key?{Authorization:'Bearer '+key}:{},signal:AbortSignal.timeout(15000)});if(!r.ok){const retry=r.headers.get('retry-after');if(retry)res.setHeader('Retry-After',retry);return res.status(r.status).json({error:'Wallet API unavailable'});}const payload=await r.json();res.setHeader('Cache-Control','private, no-store');return res.json({data:payload.data});}catch{return res.status(502).json({error:'Wallet API unavailable'});}
}
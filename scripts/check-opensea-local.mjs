/** Local contract checks, never a public-network mint or an OpenSea indexing test.
 * Install solc@0.8.24, @openzeppelin/contracts@5.2.0, ethers@6 and ganache@7
 * into an isolated prefix and pass that prefix as ISLANDS_EVM_DEPENDENCIES.
 */
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const root=fileURLToPath(new URL('../',import.meta.url));
const dependencies=process.env.ISLANDS_EVM_DEPENDENCIES||root;
const require=createRequire(resolve(dependencies,'package.json'));
const solc=require('solc'),ganache=require('ganache');
const {BrowserProvider,ContractFactory,ZeroAddress}=require('ethers');
const compilerInput={language:'Solidity',sources:{'contracts/Islands.sol':{content:readFileSync(`${root}contracts/Islands.sol`,'utf8')}},settings:{outputSelection:{'*':{'*':['abi','evm.bytecode.object']}}}};
const compiled=JSON.parse(solc.compile(JSON.stringify(compilerInput),{import:path=>{
 try{return {contents:readFileSync(path.startsWith('contracts/')?resolve(root,path):resolve(dependencies,'node_modules',path),'utf8')}}catch{return {error:'Missing dependency '+path}}
}}));
const errors=(compiled.errors||[]).filter(e=>e.severity==='error');assert.deepEqual(errors,[]);
const artifact=compiled.contracts['contracts/Islands.sol'].Islands;
const creator='0xfc5708cb64604dcf6f62de5d63a051ed577e10c1';
// Local-only impersonation; no creator private key or public RPC is used.
const rpc=ganache.provider({chain:{chainId:1337},wallet:{totalAccounts:3,unlockedAccounts:[creator]},logging:{quiet:true}});
const checks=[];
try{
 await rpc.request({method:'evm_setAccountBalance',params:[creator,'0x56BC75E2D63100000']});
 const provider=new BrowserProvider(rpc),deployer=await provider.getSigner(0),owner=await provider.getSigner(creator),buyer=await provider.getSigner(1),nextBuyer=await provider.getSigner(2);
 const buyerAddress=await buyer.getAddress();
 const deployed=await new ContractFactory(artifact.abi,artifact.evm.bytecode.object,deployer).deploy();await deployed.waitForDeployment();
 const collection=deployed.connect(owner);
 assert.equal(await collection.keyMintEnabled(),false);
 assert.notEqual((await deployer.getAddress()).toLowerCase(),creator);
 assert.equal((await collection.owner()).toLowerCase(),creator);
 await assert.rejects(()=>deployed.issue.staticCall(buyerAddress,9000n,'ipfs://deployer'));
 await assert.rejects(()=>deployed.setContractURI.staticCall('ipfs://deployer'));
 await assert.rejects(()=>deployed.transferOwnership.staticCall(deployer.address));
 checks.push('Confirmed creator is the initial collection owner even when another wallet deploys; deployer has no owner privileges');
 for(const id of ['0x80ac58cd','0x5b5e139f','0x2a55205a'])assert.equal(await collection.supportsInterface(id),true);
 checks.push('ERC-721, metadata and ERC-2981 interfaces are advertised');
 assert.equal(await collection.CREATOR_FEE_BPS(),1000n);
 for(const price of [0n,1n,9999n,10000n,500000n,10n**18n]){
  const [recipient,amount]=await collection.royaltyInfo(9001n,price);
  assert.equal(recipient.toLowerCase(),creator);assert.equal(amount,price/10n);
 }
 checks.push('10% royalty and the configured creator recipient, including rounding boundaries');
 const collectionURI='https://islands-kappa.vercel.app/nft/collection.json';
 assert.equal(await collection.contractURI(),collectionURI);
 const collectionMetadata=JSON.parse(readFileSync(`${root}public/nft/collection.json`,'utf8'));
 assert.equal(collectionMetadata.seller_fee_basis_points,1000);assert.equal(collectionMetadata.fee_recipient,creator);
 checks.push('contractURI returns the prepared collection metadata and matching preferred fee');
 for(const [tokenId,artworkId] of [[9001n,'000056-N'],[9002n,'000056-S']]){
  const uri=`https://islands-kappa.vercel.app/nft/${artworkId}.json`;
  const receipt=await (await collection.issue(await buyer.getAddress(),tokenId,uri)).wait();
  assert.equal(await collection.ownerOf(tokenId),await buyer.getAddress());assert.equal(await collection.tokenURI(tokenId),uri);
  const transfer=receipt.logs.map(log=>{try{return collection.interface.parseLog(log)}catch{return null}}).find(log=>log?.name==='Transfer');
  assert.equal(transfer.args.from,ZeroAddress);assert.equal(transfer.args.to,await buyer.getAddress());assert.equal(transfer.args.tokenId,tokenId);
  const metadata=JSON.parse(readFileSync(`${root}public/nft/${artworkId}.json`,'utf8'));
  assert.ok(metadata.name.includes(artworkId));assert.ok(metadata.image.startsWith('https://'));
 }
 checks.push('Local N/S issuance emits Transfer from zero and returns the intended owner and JSON URI');
 await (await collection.connect(buyer).transferFrom(buyerAddress,await nextBuyer.getAddress(),9002n)).wait();
 assert.equal(await collection.ownerOf(9002n),await nextBuyer.getAddress());
 assert.equal((await collection.owner()).toLowerCase(),creator);
 const [royaltyAfterTransfer,feeAfterTransfer]=await collection.royaltyInfo(9002n,10000n);
 assert.equal(royaltyAfterTransfer.toLowerCase(),creator);assert.equal(feeAfterTransfer,1000n);
 checks.push('An NFT transfer changes its holder without changing collection ownership or the 10% creator recipient');
 await assert.rejects(()=>collection.connect(buyer).issue.staticCall(buyerAddress,9003n,'ipfs://unauthorized'));
 await assert.rejects(()=>collection.issue.staticCall(buyerAddress,9001n,'ipfs://duplicate'));
 await assert.rejects(()=>collection.tokenURI(9999n));
 checks.push('Unauthorized issuance, duplicate token IDs and nonexistent token URIs are rejected');
 await assert.rejects(()=>collection.connect(buyer).setContractURI.staticCall('ipfs://unauthorized'));
 await assert.rejects(()=>collection.setContractURI.staticCall(''));
 const updated=await (await collection.setContractURI('ipfs://collection-test')).wait();
 assert.equal(await collection.contractURI(),'ipfs://collection-test');
 assert.ok(updated.logs.some(log=>{try{return collection.interface.parseLog(log)?.name==='ContractURIUpdated'}catch{return false}}));
 checks.push('Only the owner can change collection metadata; empty URI is rejected and update event emitted');
 const names=new Set(artifact.abi.filter(x=>x.type==='function').map(x=>x.name));
 const report={network:'Local Ganache, chain ID 1337',compiler:solc.version(),public_network_transactions:0,local_checks:checks,local_checks_passed:checks.length,creator_fee_basis_points:1000,creator_fee_recipient:creator,creator_fee_enforcement_compatible:['getTransferValidator','getTransferValidationFunction','setTransferValidator'].every(name=>names.has(name)),direct_key_mint_implemented:names.has('mintWithKey'),key_mint_enabled_on_local_deployment:await collection.keyMintEnabled(),public_paid_mint_live:false,opensea_indexing_verified:false,opensea_collection_settings_verified:false,release_ready:false,blockers:['No deployed collection address is configured in this project.','Direct KEY settlement is implemented in the draft; released production inventory, verified KEY token, wallet UI, discounts and blind/regional mint paths are not complete.','A real minted token must still be checked on OpenSea for image, traits and collection association.','OpenSea Studio must still confirm 10% creator earnings and the intended recipient.','The current ERC-721/2981 draft has no creator-token transfer validator; OpenSea fee enforcement is not prepared.']};
 const output=process.argv[2];if(output)writeFileSync(output,JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));
}finally{await rpc.disconnect()}


import json,os
from pathlib import Path
from hashlib import sha256
root=Path(__file__).resolve().parents[1]
out={'chainId':84532,'compilerVersion':'0.8.24','sourceCommit':os.environ.get('GITHUB_SHA','unknown')}
for name,kind in [('IslandsTestSuite','suite'),('IslandsTestKey','key'),('IslandsTestCollection','collection')]:
    data=json.loads((root/'out'/'IslandsTestnet.sol'/(name+'.json')).read_text())
    bytecode=data['bytecode']['object']
    if not bytecode.startswith('0x'):bytecode='0x'+bytecode
    runtime=data['deployedBytecode']['object'].removeprefix('0x')
    assert len(runtime)//2<=24576, name+' runtime too large'
    assert len(bytecode.removeprefix('0x'))//2<=49152, name+' initcode too large'
    out[kind]={'abi':data['abi'],'bytecode':bytecode}
out['bundleSha256']=sha256(json.dumps(out,sort_keys=True).encode()).hexdigest()
target=root/'public'/'testnet'/'artifacts.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(out,separators=(',',':'))+'\n')
print('Exported compiled Base Sepolia test suite:',out['bundleSha256'])

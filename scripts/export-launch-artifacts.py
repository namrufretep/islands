import json, os
from pathlib import Path
from hashlib import sha256

root=Path(__file__).resolve().parents[1]
build=Path(os.environ.get('ISLANDS_FORGE_OUT',str(root/'out')))
data=json.loads((build/'IslandsLaunch.sol'/'IslandsLaunch.json').read_text())
bytecode=data['bytecode']['object']
if not bytecode.startswith('0x'):bytecode='0x'+bytecode
runtime=data['deployedBytecode']['object'].removeprefix('0x')
assert len(runtime)//2<=24576, 'Runtime exceeds EIP-170'
assert len(bytecode.removeprefix('0x'))//2<=49152, 'Initcode exceeds EIP-3860'
sources={p.name:sha256(p.read_bytes()).hexdigest() for p in sorted((root/'contracts').glob('*.sol'))}
out={'status':'candidate_not_deployed','chainId':8453,'compilerVersion':'0.8.24','optimizerRuns':200,'sourceSha256':sources,'abi':data['abi'],'bytecode':bytecode,'initcodeBytes':len(bytecode.removeprefix('0x'))//2,'runtimeBytes':len(runtime)//2}
target=root/'public'/'launch'/'artifacts.json';target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(out,separators=(',',':'))+'\n')
print('Exported checked launch candidate:',out['initcodeBytes'],'initcode bytes;',out['runtimeBytes'],'runtime bytes')

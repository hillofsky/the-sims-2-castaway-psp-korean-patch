"""Apply a Castaway copy/literal patch using only Python's standard library."""
import argparse,hashlib,json,os,zipfile
from pathlib import Path

def hash_file(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def apply(source,patch,output):
    source,patch,output=map(Path,(source,patch,output))
    if source.resolve()==output.resolve() or output.exists():raise ValueError('Output must be a new file distinct from original')
    with zipfile.ZipFile(patch) as z:
        metadata=z.getinfo('patch.json');literals=z.getinfo('literals.bin')
        if metadata.file_size>16*1024*1024 or literals.file_size>128*1024*1024:raise ValueError('Patch exceeds size limits')
        manifest=json.loads(z.read(metadata));blob=z.read(literals)
    if manifest.get('format')!='castaway-copy-literal-v1':raise ValueError('Unsupported patch format')
    if source.stat().st_size!=manifest['source_size'] or hash_file(source)!=manifest['source_sha256']:raise ValueError('Original ISO hash mismatch')
    if hashlib.sha256(blob).hexdigest()!=manifest['literal_sha256']:raise ValueError('Literal payload hash mismatch')
    if not 0<manifest['target_size']<2*1024*1024*1024 or len(manifest['operations'])>100000:raise ValueError('Invalid target or operation limit')
    for op in manifest['operations']:
        if op['kind'] not in ('copy','literal') or any(not isinstance(op[k],int) or op[k]<0 for k in ('output','offset','length')):raise ValueError('Invalid patch operation')
        if op['output']+op['length']>manifest['target_size']:raise ValueError('Output range outside target')
        limit=manifest['source_size'] if op['kind']=='copy' else len(blob)
        if op['offset']+op['length']>limit:raise ValueError('Input range outside source')
    output.parent.mkdir(parents=True,exist_ok=True)
    partial=output.with_name(output.name+'.partial.'+str(os.getpid()))
    with source.open('rb') as src,partial.open('xb') as dst:
        dst.truncate(manifest['target_size'])
        for op in manifest['operations']:
            dst.seek(op['output'])
            if op['kind']=='literal':dst.write(blob[op['offset']:op['offset']+op['length']])
            else:
                src.seek(op['offset']);remaining=op['length']
                while remaining:
                    block=src.read(min(8*1024*1024,remaining))
                    if not block:raise ValueError('Unexpected end of source')
                    dst.write(block);remaining-=len(block)
    actual=hash_file(partial)
    if actual!=manifest['target_sha256']:raise ValueError('Patched output hash mismatch; partial output preserved')
    # No clobber: reserve destination atomically before replacing it.
    with output.open('xb'):pass
    os.replace(partial,output)
    return {'output':str(output),'sha256':actual,'status':'BUILT_UNVERIFIED','runtime':'NOT_VERIFIED'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--patch',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    print(json.dumps(apply(a.source,a.patch,a.output),ensure_ascii=True,indent=2))

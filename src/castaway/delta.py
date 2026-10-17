"""Experimental source-copy/literal patch writer; never embeds unchanged game data."""
import hashlib,json,struct,zipfile
from pathlib import Path
from .iso9660 import Iso9660
from .arc import read_arc
from .quickdat import string_table
from .font import parse_font
from .dataset import parse_dataset

def sha256_file(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):digest.update(block)
    return digest.hexdigest()

class Emitter:
    def __init__(self,source):
        self.source=source;self.position=0;self.ops=[];self.literal=bytearray()
    def copy(self,offset,expected):
        self.source.seek(offset)
        if self.source.read(len(expected))!=expected:raise ValueError('Provenance copy mismatch')
        self._op('copy',offset,len(expected));self.position+=len(expected)
    def lit(self,data):
        if not data:return
        offset=len(self.literal);self.literal.extend(data)
        self._op('literal',offset,len(data));self.position+=len(data)
    def _op(self,kind,offset,length):
        if not length:return
        if self.ops:
            old=self.ops[-1]
            if old['kind']==kind and old['output']+old['length']==self.position and old['offset']+old['length']==offset:
                old['length']+=length;return
        self.ops.append({'kind':kind,'output':self.position,'offset':offset,'length':length})

def emit_font(e,old,new,source_offset):
    a,b=parse_font(old),parse_font(new);start=e.position
    e.lit(new[:b['start']]);e.lit(b['data'][:b['defs']])
    old_glyph_bytes=a['count']*a['stride']
    new_old_glyph_bytes=a['count']*b['stride']
    first_records=b['data'][b['defs']:b['defs']+new_old_glyph_bytes]
    if a['stride']==b['stride'] and first_records==a['data'][a['defs']:a['defs']+old_glyph_bytes]:e.copy(source_offset+a['start']+a['defs'],first_records)
    else:e.lit(first_records)
    new_end=b['defs']+b['count']*b['stride']
    e.lit(b['data'][b['defs']+new_old_glyph_bytes:new_end])
    old_end=a['defs']+old_glyph_bytes
    e.copy(source_offset+a['start']+old_end,b['data'][new_end:b['bmp']-32])
    e.lit(b['data'][b['bmp']-32:b['bmp']+16])
    pixels=b['data'][b['bmp']+16:b['bmp']+16+b['pixel_size']]
    old_stride=a['width']//2;new_stride=b['width']//2
    for y in range(a['height']):
        e.copy(source_offset+a['start']+a['bmp']+16+y*old_stride,pixels[y*new_stride:y*new_stride+old_stride])
        e.lit(pixels[y*new_stride+old_stride:(y+1)*new_stride])
    e.lit(pixels[a['height']*new_stride:])
    e.copy(source_offset+a['start']+a['bmp']+16+a['pixel_size'],b['data'][b['bmp']+16+b['pixel_size']:])
    if e.position-start!=len(new):raise ValueError('Font provenance length mismatch')

def emit_quickdat(e,old,new,source_offset):
    start=e.position;first=struct.unpack_from('<I',new,4)[0];count=first//24
    e.lit(new[:first]);bias=struct.unpack_from('<I',old,8)[0]
    for i in range(count):
        _,os,oz,orel,orz,_=struct.unpack_from('<6I',old,i*24)
        _,ns,nz,nrel,nrz,_=struct.unpack_from('<6I',new,i*24)
        if e.position-start!=ns:raise ValueError('Quickdat position mismatch')
        a,b=old[os:os+oz],new[ns:ns+nz]
        if a==b:e.copy(source_offset+os,b)
        else:
            ae,_=string_table(a,bias);be,_=string_table(b,bias)
            if len(ae)!=len(be):raise ValueError('String count changed')
            e.lit(b[:be[0][0]])
            for (ao,az,at),(bo,bz,bt) in zip(ae,be):
                raw=b[bo:bo+bz]
                if at==bt and raw==a[ao:ao+bz]:e.copy(source_offset+os+ao,raw)
                else:e.lit(raw)
        e.lit(new[ns+nz:nrel])
        relocation=new[nrel:nrel+nrz]
        if relocation==old[orel:orel+orz]:e.copy(source_offset+orel,relocation)
        else:e.lit(relocation)
    if e.position-start!=len(new):raise ValueError('Quickdat provenance length mismatch')

def emit_dataset(e,old,new,source_offset):
    start=e.position;_,header,entries=parse_dataset(new);_,_,original_entries=parse_dataset(old)
    originals={x['index']:x for x in original_entries};e.lit(new[:header])
    for entry in sorted(entries,key=lambda x:x['offset']):
        original=originals[entry['index']]
        a=old[original['offset']:original['offset']+original['size']]
        b=new[entry['offset']:entry['offset']+entry['size']]
        if e.position-start!=entry['offset']:raise ValueError('Dataset provenance position mismatch')
        if a==b:e.copy(source_offset+original['offset'],b)
        elif entry['kind']=='QuickDatas':emit_quickdat(e,a,b,source_offset+original['offset'])
        elif entry['kind']=='Textures':e.lit(b)
        else:raise ValueError('Unsupported changed dataset asset')
    if e.position-start!=len(new):raise ValueError('Dataset provenance length mismatch')

def emit_sparse(e,old,new,source_offset):
    if len(old)!=len(new):raise ValueError('Sparse metadata size changed')
    for pos in range(0,len(new),64):
        chunk=new[pos:pos+64]
        if chunk==old[pos:pos+64]:e.copy(source_offset+pos,chunk)
        else:e.lit(chunk)

def emit_arc(e,old,new,source_offset,kind):
    start=e.position;old_entries={x[0]:x for x in read_arc(old)}
    e.lit(new[:16])
    for name,offset,payload,key in sorted(read_arc(new),key=lambda x:x[1]):
        _,old_offset,old_payload,_=old_entries[name]
        if e.position-start!=offset:raise ValueError('ARC position mismatch')
        if payload==old_payload:e.copy(source_offset+old_offset,payload)
        elif kind=='font':emit_font(e,old_payload,payload,source_offset+old_offset)
        elif kind=='dataset':emit_dataset(e,old_payload,payload,source_offset+old_offset)
        elif kind=='texture':e.lit(payload)
        else:emit_quickdat(e,old_payload,payload,source_offset+old_offset)
    footer=struct.unpack_from('<I',new)[0];e.lit(new[footer:])
    if e.position-start!=len(new):raise ValueError('ARC provenance length mismatch')

def create_patch(original,target,output):
    original,target,output=Path(original),Path(target),Path(output)
    if output.exists():raise FileExistsError(output)
    old,new=Iso9660(original),Iso9660(target)
    with original.open('rb') as source,target.open('rb') as built:
        e=Emitter(source)
        e.ops.append({'kind':'copy','output':0,'offset':0,'length':original.stat().st_size});e.position=original.stat().st_size
        paths=[path for path in old.files if new.files[path]['extent']!=old.files[path]['extent']]
        for path in sorted(paths,key=lambda p:new.files[p]['extent']):
            meta=new.files[path];start=meta['extent']*2048
            built.seek(e.position);e.lit(built.read(start-e.position))
            source_offset=old.files[path]['extent']*2048
            if path.endswith('index.ind'):emit_sparse(e,old.read(path),new.read(path),source_offset)
            elif not path.endswith('.arc'):e.lit(new.read(path))
            else:emit_arc(e,old.read(path),new.read(path),source_offset,'font' if path.endswith('fonts.arc') else 'dataset' if path.endswith('datasets.arc') else 'texture' if path.endswith('textures.arc') else 'quick')
        built.seek(e.position);e.lit(built.read())
        # Overlay ISO metadata after the initial source copy and appended resources.
        for path in paths:
            pos=old.files[path]['record_offset']+2;built.seek(pos);e.position=pos;e.lit(built.read(16))
        for sector in range(16,32):
            built.seek(sector*2048);descriptor=built.read(2048)
            if descriptor[0]==1:e.position=sector*2048+80;e.lit(descriptor[80:88])
            if descriptor[0]==255:break
    manifest={'format':'castaway-copy-literal-v1','status':'EXPERIMENTAL_RUNTIME_UNVERIFIED','source_sha256':sha256_file(original),'source_size':original.stat().st_size,'target_sha256':sha256_file(target),'target_size':target.stat().st_size,'operations':e.ops,'literal_sha256':hashlib.sha256(e.literal).hexdigest()}
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr('patch.json',json.dumps(manifest,ensure_ascii=True,separators=(',',':')))
        z.writestr('literals.bin',e.literal)
    return {'operations':len(e.ops),'literal_bytes':len(e.literal),'zip_bytes':output.stat().st_size,'target_sha256':manifest['target_sha256']}

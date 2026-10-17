"""Quickdat UTF-16 language table with relocation bias from section zero."""
import struct

def string_table(section, bias):
    first=struct.unpack_from('<I',section)[0]-bias
    if first<=0 or first%4 or first>len(section): raise ValueError('Invalid pointer table length')
    pointers=list(struct.unpack_from('<%dI'%(first//4),section))
    offsets=[p-bias for p in pointers]
    if offsets[0]!=first or any(a>b for a,b in zip(offsets,offsets[1:])): raise ValueError('Invalid pointer ordering')
    result=[];rebuilt=bytearray(section[:first])
    for i,offset in enumerate(offsets):
        end=offsets[i+1] if i+1<len(offsets) else len(section)
        raw=section[offset:end]
        if len(raw)%2: raise ValueError('Odd string allocation')
        terminator=next((j for j in range(0,len(raw),2) if raw[j:j+2]==b'\x00\x00'),None)
        if terminator is None: raise ValueError('Missing UTF-16 terminator')
        text=raw[:terminator].decode('utf-16le')
        padding=raw[terminator+2:]
        if any(padding): raise ValueError('Nonzero string padding')
        rebuilt.extend((text+'\x00').encode('utf-16le')+padding)
        result.append((offset,end-offset,text))
    if rebuilt!=section: raise ValueError('String table roundtrip mismatch')
    return result,bias

def rebuild_string_table(section, bias, replacements):
    entries,_=string_table(section,bias)
    if not replacements:return section
    if any(i<0 or i>=len(entries) for i in replacements):raise ValueError('Unknown string index')
    table=bytearray(len(entries)*4);pool=bytearray()
    for i,(_,_,source) in enumerate(entries):
        text=replacements.get(i,source)
        if '\x00' in text:raise ValueError('NUL inside translation')
        struct.pack_into('<I',table,i*4,bias+len(table)+len(pool))
        pool.extend((text+'\x00').encode('utf-16le'))
    return bytes(table+pool)

def rebuild_resource(payload, section_replacements):
    first=struct.unpack_from('<I',payload,4)[0]
    if first%24 or first<24:raise ValueError('Invalid quickdat section directory')
    count=first//24
    bias=struct.unpack_from('<I',payload,8)[0]
    result=bytearray(payload[:first])
    for sec in range(count):
        header,start,size,reloc,relsize,flags=struct.unpack_from('<6I',payload,sec*24)
        if header!=24 or reloc<start+size:raise ValueError('Unsupported quickdat section')
        data=payload[start:start+size]
        if sec in section_replacements:
            data=rebuild_string_table(data,bias,section_replacements[sec])
        newstart=len(result);result.extend(data)
        if section_replacements.get(sec):
            result.extend(b'\x00'*((-len(result))%4))
        else:
            result.extend(payload[start+size:reloc])
        newreloc=len(result);result.extend(payload[reloc:reloc+relsize])
        struct.pack_into('<6I',result,sec*24,header,newstart,len(data),newreloc,relsize,flags)
    if not section_replacements and result!=payload:raise ValueError('Quickdat no-change roundtrip failed')
    return bytes(result)

def common_tables(payload):
    _,start,size,_,_,_=struct.unpack_from('<6I',payload)
    data=payload[start:start+size]
    version,nameptr,count=struct.unpack_from('<3I',data)
    if version!=1 or 24+count*20>len(data):raise ValueError('Unsupported common quickdat table')
    tables=[]
    def name(offset):
        if not 0<=offset<len(data):raise ValueError('String name outside common section')
        return data[offset:data.index(0,offset)].decode('ascii')
    for i in range(count):
        n,offset,keys,rows,stride=struct.unpack_from('<5I',data,24+i*20)
        if offset+rows*stride>len(data) or stride%4:raise ValueError('Common table data outside section')
        rownames=[name(struct.unpack_from('<I',data,keys+j*4)[0]) if keys else str(j) for j in range(rows)]
        tables.append({'name':name(n),'offset':offset,'rows':rows,'stride':stride,'keys':rownames,'data':data[offset:offset+rows*stride]})
    return tables

"""TSTD dataset preload containers with 44-byte typed asset entries."""
import struct

def parse_dataset(data):
    if data[:8]!=b'\x0a\x00\x00\x00TSTD':raise ValueError('Unsupported dataset header')
    name_length=struct.unpack_from('<I',data,12)[0]
    body=20+name_length
    if struct.unpack_from('<I',data,body-4)[0]!=len(data)-body:raise ValueError('Dataset outer size mismatch')
    count=struct.unpack_from('<I',data,body+64)[0]
    table=body+68;end=table+count*44
    if count>100000 or end>len(data):raise ValueError('Invalid dataset asset count')
    entries=[]
    for i in range(count):
        pos=table+i*44;kind=data[pos:pos+32].split(b'\x00',1)[0].decode('ascii')
        key,size,offset=struct.unpack_from('<III',data,pos+32)
        if offset<end or offset+size>len(data):raise ValueError('Dataset asset outside bounds')
        entries.append({'index':i,'kind':kind,'key':key,'size':size,'offset':offset,'record':pos})
    ranges=sorted((x['offset'],x['offset']+x['size']) for x in entries)
    if ranges and (ranges[0][0]!=end or ranges[-1][1]!=len(data) or any(a[1]!=b[0] for a,b in zip(ranges,ranges[1:]))):raise ValueError('Dataset assets not exactly contiguous')
    return body,end,entries

def rebuild_dataset(data,replacements):
    body,header_end,entries=parse_dataset(data)
    if set(replacements)-{e['index'] for e in entries}:raise ValueError('Unknown dataset asset')
    output=bytearray(data[:header_end]);locations={}
    for e in sorted(entries,key=lambda x:x['offset']):
        value=replacements.get(e['index'],data[e['offset']:e['offset']+e['size']])
        locations[e['index']]=(len(value),len(output));output.extend(value)
    for e in entries:struct.pack_into('<II',output,e['record']+36,*locations[e['index']])
    struct.pack_into('<I',output,body-4,len(output)-body)
    parse_dataset(output)
    if not replacements and output!=data:raise ValueError('Dataset no-change roundtrip failed')
    return bytes(output)

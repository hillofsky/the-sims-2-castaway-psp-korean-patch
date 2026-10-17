"""ARC footer directory and deterministic serializer."""
import struct

def read_arc(data):
    if len(data)<20:raise ValueError('ARC too short')
    index=struct.unpack_from('<I',data)[0]
    count=struct.unpack_from('<I',data,index)[0]
    if count>100000:raise ValueError('Invalid ARC count')
    pos=index+4;entries=[]
    for _ in range(count):
        key,offset,size=struct.unpack_from('<III',data,pos)
        end=data.index(0,pos+12);name=data[pos+12:end].decode('ascii')
        if end+9>len(data) or offset<16 or offset+size>index:raise ValueError('Invalid ARC entry bounds')
        entries.append((name,offset,data[offset:offset+size],key));pos=end+9
    if pos!=len(data):raise ValueError('ARC directory does not consume file')
    ranges=sorted((offset,offset+len(payload)) for _,offset,payload,_ in entries)
    if ranges and (ranges[0][0]!=16 or ranges[-1][1]!=index or any(a[1]!=b[0] for a,b in zip(ranges,ranges[1:]))):raise ValueError('ARC payloads not exactly contiguous')
    return entries

def rebuild_arc(data,replacements):
    entries=read_arc(data)
    if set(replacements)-{e[0] for e in entries}:raise ValueError('Unknown ARC replacement')
    oldindex=struct.unpack_from('<I',data)[0]
    output=bytearray(data[:16]);locations={}
    for name,offset,payload,key in sorted(entries,key=lambda e:e[1]):
        value=replacements.get(name,payload)
        locations[name]=(len(output),len(value));output.extend(value)
    pos=oldindex+4;directory=[]
    for name,offset,payload,key in entries:
        end=data.index(0,pos+12);tail=data[pos+12:end+9]
        directory.append(struct.pack('<III',key,*locations[name])+tail);pos=end+9
    struct.pack_into('<I',output,0,len(output))
    output.extend(struct.pack('<I',len(entries))+b''.join(directory))
    if not replacements and output!=data:raise ValueError('ARC no-change roundtrip failed')
    read_arc(output)
    return bytes(output)

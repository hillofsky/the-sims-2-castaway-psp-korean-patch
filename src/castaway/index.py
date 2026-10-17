"""Update the global resource index after rebuilding ARC payload locations."""
import struct
from .arc import read_arc

def update_index(data,archives):
    count=struct.unpack_from('<I',data)[0]
    offsets=struct.unpack_from('<%dI'%(count+1),data,4)
    if count%2 or offsets[-1]!=len(data):raise ValueError('Invalid index chunk directory')
    result=bytearray(data);report=[]
    for i in range(0,count,2):
        name=data[offsets[i]:offsets[i+1]].rstrip(b'\x00').decode('ascii')
        if name not in archives:continue
        start,end=offsets[i+1:i+3]
        a,n,size,b,c=struct.unpack_from('<5I',data,start)
        if (a,b,c)!=(0,1,0) or size!=end-start or size!=20+n*12:raise ValueError('Unsupported global index block: '+name)
        old_arc,new_arc=archives[name]
        old={key:(off,len(p)) for _,off,p,key in read_arc(old_arc)}
        new={key:(off,len(p)) for _,off,p,key in read_arc(new_arc)}
        if len(old)!=n or old.keys()!=new.keys():raise ValueError('Index/ARC resource key mismatch')
        changed=0
        for row in range(n):
            key=struct.unpack_from('<I',data,start+20+row*4)[0]
            pos=start+20+n*4+row*8
            if struct.unpack_from('<II',data,pos)!=old[key]:raise ValueError('Original global index does not match ARC')
            struct.pack_into('<II',result,pos,*new[key]);changed+=old[key]!=new[key]
        report.append({'category':name,'resources':n,'changed_records':changed})
    if len(report)!=len(archives):raise ValueError('Missing global index categories')
    return bytes(result),report

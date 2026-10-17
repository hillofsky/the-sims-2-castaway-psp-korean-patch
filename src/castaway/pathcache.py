"""Read-only Sims2 PSP pathcache directory; no decoded filenames assumed.
Layout cross-check: https://aluigi.altervista.org/bms/sims2_psp.bms
"""
import struct

def parse_directory(data,total_size):
    magic,info_size,expected,_=struct.unpack_from('<4I',data)
    if magic!=0x1bacac8e or info_size>len(data):raise ValueError('Invalid pathcache header')
    seen=set();entries=[]
    def folder(pos,parent):
        if pos in seen:raise ValueError('Directory cycle')
        seen.add(pos)
        name,table,nfolders,nfiles=struct.unpack_from('<IIHH',data,pos)
        path=parent+'/'+str(name)
        if table+12*(nfolders+nfiles)>info_size:raise ValueError('Directory outside metadata')
        for i in range(nfolders):folder(table+i*12,path)
        for i in range(nfiles):
            name,sector,size=struct.unpack_from('<III',data,table+(nfolders+i)*12)
            offset=sector*2048
            if offset+size>total_size:raise ValueError('Resource outside archive')
            entries.append({'path':path+'/'+str(name),'name_offset':name,'offset':offset,'size':size})
    folder(16,'')
    if len(entries)+len(seen)-1!=expected:raise ValueError('File count mismatch: '+str(len(entries))+' dirs '+str(len(seen))+' vs '+str(expected))
    return entries





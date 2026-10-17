import sys,struct,re
from pathlib import Path
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
p=next(p for n,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/quickdat.arc')) if n=='urbzui')
for i in range(22):
 desc=struct.unpack_from('<6I',p,i*24);print('SECTION',i,desc)
 if i in (1,2,3,10,11,12):
  start=desc[1];print(p[start:start+240].hex());print(repr(p[start:start+240].decode('utf-16le','replace')))
for pat in (b'T\x00h\x00e\x00r\x00e',b'\x00T\x00h\x00e\x00r\x00e',b'There',b'There is no data.'):
 print(pat,p.find(pat))

import sys,struct
from pathlib import Path
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
p=next(p for n,o,p,k in read_arc(Iso9660(project_path(root,'original_iso')).read('/PSP_GAME/USRDIR/data/quickdat.arc')) if n=='urbzui')
s=p[64240:298036]
for at in (11700,11712,11716,11728):print(at,repr(s[at:at+100].decode('utf-16le','replace')))
print('u32 pre',struct.unpack_from('<12I',s,11664))

import sys,struct,json,re
from pathlib import Path
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
p=next(p for n,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/quickdat.arc')) if n=='urbzui')
for i in (1,2,14,21):
 _,start,size,_,_,_=struct.unpack_from('<6I',p,i*24); section=p[start:start+size]; ptr=struct.unpack_from('<I',section)[0]
 print('section',i,'firstptr',ptr,'count?',ptr//4)
 for addr in (ptr,ptr+start,99356):
  print('addr',addr,repr(p[addr:addr+120].decode('utf-16le','replace')))
 for m in list(re.finditer(rb'(?:[\x20-\x7e]\x00){7,}',section))[:12]:print(m.start(),m.group().decode('utf-16le'))
 for target in ('There is no data.', 'There is no', 'Load Game', 'New Game'):
  at=section.find(target.encode('utf-16le'))
  print(target,at)

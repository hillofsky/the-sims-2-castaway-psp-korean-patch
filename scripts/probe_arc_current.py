import sys,struct,re
from pathlib import Path
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
iso=Iso9660(project_path(root,'original_iso'))
for n in ('fonts.arc','soundtra.arc','binaries.arc','quickdat.arc','datasets.arc'):
 d=iso.read('/PSP_GAME/USRDIR/data/'+n); index=struct.unpack_from('<I',d)[0]
 print(n,len(d),'index',index,'tail',d[index:index+96].hex())
 for m in list(re.finditer(rb'[ -~]{5,}',d))[:8]:print(m.start(),repr(m.group()[:100]))

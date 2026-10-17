import sys,struct,json
from pathlib import Path
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
quick={n:p for n,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/quickdat.arc'))}
reports=[]
for n,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/datasets.arc')):
 for q,d in quick.items():
  pos=p.find(d[:128])
  while pos>=0:
   if p[pos:pos+len(d)]==d:reports.append({'dataset':n,'dataset_offset':o,'quickdat':q,'offset_in_dataset':pos,'size':len(d)})
   pos=p.find(d[:128],pos+1)
(root/'logs'/'STEP_010'/'embedded_quickdat.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps(reports,indent=2))

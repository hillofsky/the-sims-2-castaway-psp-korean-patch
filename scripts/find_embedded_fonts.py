import sys,json
from pathlib import Path
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
fonts={n:p for n,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/fonts.arc'))}
report=[]
for arcpath in ('/PSP_GAME/USRDIR/data/datasets.arc','/PSP_GAME/USRDIR/data/binaries.arc'):
 for n,o,p,k in read_arc(iso.read(arcpath)):
  for font,d in fonts.items():
   magic=d.index(b'FntM');blob=d[magic:];pos=p.find(blob[:128])
   while pos>=0:
    if p[pos:pos+len(blob)]==blob:report.append({'archive':arcpath,'resource':n,'font':font,'resource_offset':o,'font_offset':pos,'size':len(blob),'whole_payload_offset':p.find(d)})
    pos=p.find(blob[:128],pos+1)
(root/'logs'/'STEP_010'/'embedded_fonts.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

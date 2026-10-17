import sys,struct,re,collections,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
report=[]
for name,offset,payload,key in read_arc(iso.read('/PSP_GAME/USRDIR/data/quickdat.arc')):
 print(name,len(payload),'u32',struct.unpack_from('<24I',payload))
 if name!='urbzui':continue
 for start in (0,24,512,536,struct.unpack_from('<I',payload,8)[0],struct.unpack_from('<I',payload,12)[0]):
  print('at',start,payload[start:start+96].hex())
 matches=list(re.finditer(rb'[ -~]{8,}',payload))
 print('ascii count',len(matches),'samples',[(m.start(),m.group()[:80].decode('ascii')) for m in matches[:40]])
 report.append({'name':name,'ascii_samples':[(m.start(),m.group()[:200].decode('ascii')) for m in matches[:200]]})
(root/'logs'/'STEP_009_inventory'/'quickdat_probe.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

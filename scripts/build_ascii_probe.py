import sys,csv,struct,shutil,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
from castaway.quickdat import string_table
original=project_path(root,'original_iso')
iso=Iso9660(original);arcpath='/PSP_GAME/USRDIR/data/quickdat.arc'
arc=iso.read(arcpath);name,resource_offset,payload,key=next(e for e in read_arc(arc) if e[0]=='urbzui')
changes=[]
for sec in (1,2):
 _,start,size,_,_,_=struct.unpack_from('<6I',payload,sec*24)
 entries,bias=string_table(payload[start:start+size],struct.unpack_from('<I',payload,8)[0])
 for idx,(offset,allocated,text) in enumerate(entries):
  if text=='Start New Game':changes.append({'section':sec,'index':idx,'offset':iso.files[arcpath]['extent']*2048+resource_offset+start+offset,'source':text,'target':'ASCII TEST NOW'})
if len(changes)!=2:raise ValueError('Expected one New Game in each English section')
target=root/'build'/'CASTAWAY_STEP010_ASCII.iso'
if target.exists():raise FileExistsError(target)
shutil.copyfile(original,target)
with target.open('r+b') as f:
 for c in changes:
  f.seek(c['offset']);assert f.read(28)==c['source'].encode('utf-16le')
  f.seek(c['offset']);f.write(c['target'].encode('utf-16le'))
with original.open('rb') as a,target.open('rb') as b:
 actual=[];base=0
 while True:
  x=a.read(4*1024*1024);y=b.read(4*1024*1024)
  if not x and not y:break
  if len(x)!=len(y):raise ValueError('ISO size changed')
  actual.extend(base+i for i,(j,k) in enumerate(zip(x,y)) if j!=k);base+=len(x)
allowed={c['offset']+i for c in changes for i in range(28)}
if not set(actual)<=allowed or not actual:raise ValueError('Mutation isolation failed')
report={'output':str(target),'changes':changes,'changed_bytes':len(actual),'mismatch_offsets':actual,'status':'BUILT_UNVERIFIED'}
(root/'logs'/'STEP_010'/'ascii_build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))


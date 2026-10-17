import sys,json,shutil,struct
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
original=project_path(root,'original_iso');target=root/'build'/'CASTAWAY_STEP017_ASCII_CLONES.iso'
if target.exists():raise FileExistsError(target)
iso=Iso9660(original);source='Start New Game';replacement='ASCII TEST NOW';needle=(source+'\0').encode('utf-16le');hits=[]
for path in ('/PSP_GAME/USRDIR/data/quickdat.arc','/PSP_GAME/USRDIR/data/datasets.arc'):
 data=iso.read(path);pos=0
 while True:
  pos=data.find(needle,pos)
  if pos<0:break
  hits.append(iso.files[path]['extent']*2048+pos);pos+=len(needle)
if len(hits)!=4:raise ValueError('Expected four exact English original strings')
shutil.copyfile(original,target)
with target.open('r+b') as f:
 for offset in hits:f.seek(offset);f.write(replacement.encode('utf-16le'))
actual=[];base=0
with original.open('rb') as a,target.open('rb') as b:
 while True:
  x,y=a.read(8*1024*1024),b.read(8*1024*1024)
  if not x and not y:break
  if x!=y:actual.extend(base+i for i,(v,w) in enumerate(zip(x,y)) if v!=w)
  base+=len(x)
if not set(actual)<={offset+i for offset in hits for i in range(28)}:raise ValueError('Unintended ISO mutation')
report={'hits':hits,'changed_bytes':len(actual),'output':str(target),'runtime':'NOT_VERIFIED'}
(root/'logs'/'STEP_010'/'ascii_clone_build.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True))

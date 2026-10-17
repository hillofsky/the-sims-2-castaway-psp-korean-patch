import sys,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
iso=Iso9660(project_path(root,'original_iso'))
patterns={'utf16le':'Start New Game'.encode('utf-16le'),'ascii':b'Start New Game','upper_utf16le':'START NEW GAME'.encode('utf-16le')};matches=[]
with Path(iso.path).open('rb') as f:
 base=0;overlap=b''
 while True:
  block=f.read(8*1024*1024)
  if not block:break
  data=overlap+block;data_base=base-len(overlap)
  for label,pattern in patterns.items():
   at=0
   while True:
    at=data.find(pattern,at)
    if at<0:break
    absolute=data_base+at
    if absolute+len(pattern)>base:
     file=next((n for n,e in iso.files.items() if e['extent']*2048<=absolute<e['extent']*2048+e['size']),None)
     matches.append({'encoding':label,'offset':absolute,'file':file,'file_offset':absolute-iso.files[file]['extent']*2048 if file else None})
    at+=len(pattern)
  overlap=data[-128:];base+=len(block)
(root/'logs'/'STEP_010'/'new_game_source_hits.json').write_text(json.dumps(matches,indent=2),encoding='utf-8');print(json.dumps(matches,indent=2))

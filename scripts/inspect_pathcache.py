import sys,struct,csv,json,collections
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.pathcache import parse_directory
iso=Iso9660(project_path(root,'reference_iso'));entry=iso.files['/PSP_GAME/USRDIR/pathcache.bin'];base=entry['extent']*2048
rows=[];fonts=[]
with Path(iso.path).open('rb') as f:
 f.seek(base);header=f.read(16);info_size=struct.unpack_from('<I',header,4)[0];f.seek(base);metadata=f.read(info_size)
 entries=parse_directory(metadata,entry['size'])
 for e in entries:
  f.seek(base+e['offset']);data=f.read(min(512,e['size']))
  namehex=metadata[e['name_offset']:e['name_offset']+32].hex()
  rows.append([e['path'],e['offset'],e['size'],namehex,data[:64].hex()])
  if any(s in data for s in (b'FntMP5',b'PGF0',b'TNOF',b'FONT',b'font',b'.pgf',b'.ttf')):fonts.append(dict(e,header=data.hex()))
out=root/'logs'/'STEP_011'
with (out/'pathcache_entries.tsv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['path_ids','offset','size','raw_name_hex','header_hex']);w.writerows(rows)
(out/'font_candidates.json').write_text(json.dumps(fonts,indent=2),encoding='utf-8')
print(json.dumps({'entries':len(entries),'font_candidates':len(fonts),'candidates':fonts[:5]},indent=2))

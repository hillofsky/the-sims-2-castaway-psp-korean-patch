import sys,struct,re,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
iso=Iso9660(project_path(root,'reference_iso'));meta=iso.files['/PSP_GAME/USRDIR/pathcache.bin']
with Path(iso.path).open('rb') as f:
 f.seek(meta['extent']*2048);data=f.read(1024*1024)
report={'header_u32':struct.unpack_from('<32I',data),'strings':[]}
for m in re.finditer(rb'[ -~]{6,}',data):
 if any(x in m.group().lower() for x in (b'font',b'korean',b'kor_',b'locale',b'path',b'.arc',b'.fnt',b'main')):
  report['strings'].append([m.start(),m.group().decode('ascii')])
(root/'logs'/'STEP_011'/'pathcache_probe.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('header',report['header_u32']);print('strings',report['strings'][:40])
for at in (0,0x8f384,0x41f3,0x2ee00,0x17380,0x17388,0x1738e):
 print(hex(at),data[at:at+128].hex())

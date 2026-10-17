import sys,struct,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
from castaway.pathcache import parse_directory
out=root/'logs'/'STEP_011'
ko=Iso9660(project_path(root,'reference_iso'));meta=ko.files['/PSP_GAME/USRDIR/pathcache.bin'];base=meta['extent']*2048
with Path(ko.path).open('rb') as f:
 f.seek(base);header=f.read(16);f.seek(base);metadata=f.read(struct.unpack_from('<I',header,4)[0]);entries=parse_directory(metadata,meta['size'])
 e=next(x for x in entries if x['name_offset']==203304);f.seek(base+e['offset']);data=f.read(e['size'])
# header directory tag has 4-byte tag + u16 type + u16 alignment
print('Korean res header',struct.unpack_from('<13I',data));print('font positions',[m.start() for m in re.finditer(b'font',data)])
strings=[]
for m in re.finditer(rb'[ -~]{5,}',data):
 if any(t in m.group().lower() for t in (b'font',b'trebu',b'korea',b'hangul',b'interface',b'.ttf',b'.pgf')):strings.append([m.start(),m.group().decode('ascii')])
print('font names',strings[:30])
(out/'ko_font_resource_probe.json').write_text(json.dumps({'entry':e,'font_strings':strings,'header':data[:512].hex(),'tail':data[-256:].hex()},indent=2),encoding='utf-8')
original=Iso9660(project_path(root,'original_iso'))
font_report=[]
for name,offset,payload,key in read_arc(original.read('/PSP_GAME/USRDIR/data/fonts.arc')):
 pos=payload.find(b'FntMP5');font_report.append({'name':name,'size':len(payload),'fntmp5_offset':pos,'header':payload[:256].hex(),'magic_header':payload[pos:pos+160].hex() if pos>=0 else ''})
(out/'castaway_font_probe.json').write_text(json.dumps(font_report,indent=2),encoding='utf-8');print([(f['name'],f['size'],f['fntmp5_offset']) for f in font_report])

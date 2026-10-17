import sys,json,csv,struct,hashlib,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc,rebuild_arc
from castaway.quickdat import rebuild_resource,string_table
parser=argparse.ArgumentParser();parser.add_argument('--build-id',default='STEP015');args=parser.parse_args()
if not args.build_id.replace('_','').isalnum():raise ValueError('Invalid build ID')
iso=Iso9660(project_path(root,'original_iso'))
report={'arc_roundtrip':[],'quickdat_roundtrip':[]}
for path in iso.files:
 if path.endswith('.arc') and not path.endswith(('audiostr.arc','effectss.arc')):
  d=iso.read(path);assert rebuild_arc(d,{})==d;report['arc_roundtrip'].append(path)
quick=iso.read('/PSP_GAME/USRDIR/data/quickdat.arc')
resources={n:p for n,o,p,k in read_arc(quick)}
for name,p in resources.items():
 assert rebuild_resource(p,{})==p;report['quickdat_roundtrip'].append(name)
with (root/'translation'/'text_master.tsv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
replacements={}
for r in rows:
 if r['ko_current']:replacements.setdefault(r['resource_id'],{})[int(r['string_index'])]=r['ko_current']
changed={}
for name,table in replacements.items():
 changed[name]=rebuild_resource(resources[name],{1:table,2:table})
 # Prove each translated string is parseable and precisely equals requested value.
 for sec in (1,2):
  _,start,size,_,_,_=struct.unpack_from('<6I',changed[name],sec*24)
  entries,_=string_table(changed[name][start:start+size],struct.unpack_from('<I',changed[name],8)[0])
  for idx,text in table.items():assert entries[idx][2]==text
out=rebuild_arc(quick,changed)
(root/'build'/('quickdat_'+args.build_id+'_DRAFT.arc')).write_bytes(out)
report.update(original_size=len(quick),new_size=len(out),delta=len(out)-len(quick),translations=sum(map(len,replacements.values())),output_sha256=hashlib.sha256(out).hexdigest(),runtime='NOT_TESTED')
(root/'logs'/args.build_id).mkdir(exist_ok=True)
(root/'logs'/args.build_id/'rebuild_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))


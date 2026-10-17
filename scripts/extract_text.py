import sys,struct,csv,json,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
from castaway.quickdat import string_table
iso=Iso9660(project_path(root,'original_iso'))
rows=[];reports=[]
existing={}
master=root/'translation'/'text_master.tsv'
if master.exists():
 with master.open(encoding='utf-8-sig',newline='') as f:
  existing={r['id']:r for r in csv.DictReader(f,delimiter='\t')}
for name,arc_offset,payload,key in read_arc(iso.read('/PSP_GAME/USRDIR/data/quickdat.arc')):
 first=struct.unpack_from('<I',payload,4)[0]
 if first==24:continue
 count=first//24
 for section_id in range(1,count):
  _,start,size,reloc,rsize,flags=struct.unpack_from('<6I',payload,section_id*24)
  try:
   entries,bias=string_table(payload[start:start+size],struct.unpack_from('<I',payload,8)[0])
   reports.append({'name':name,'section':section_id,'status':'PASS','count':len(entries),'bias':bias,'sha256':hashlib.sha256(payload[start:start+size]).hexdigest()})
   if section_id==1:
    for idx,(offset,allocated,text) in enumerate(entries):
     rows.append([f'TXT_{name}_{idx:05d}','quickdat.arc',name,idx,section_id,start+offset,allocated-2,text,'','utf-16le','EXTRACTED','Pointer table roundtrip PASS; language section 1, English observed.'])
  except Exception as e:reports.append({'name':name,'section':section_id,'status':'FAIL','error':str(e)})
for row in rows:
 old=existing.get(row[0])
 if old:
  if old['source_text']!=row[7]: raise ValueError('Source changed for existing ID: '+row[0])
  row[8]=old['ko_current'];row[10]=old['status'];row[11]=old['notes']
 row.extend((old or {}).get(k,'') for k in ('category','context_key','context_field'))
out=root/'logs'/'STEP_009_inventory'
(out/'quickdat_validation.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
with (root/'translation'/'text_master.tsv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['id','source_file','resource_id','string_index','section','offset','max_bytes','source_text','ko_current','encoding','status','notes','category','context_key','context_field']);w.writerows(rows)
print(json.dumps({'english_rows':len(rows),'pass':sum(r['status']=='PASS' for r in reports),'failure_count':sum(r['status']=='FAIL' for r in reports)},indent=2))




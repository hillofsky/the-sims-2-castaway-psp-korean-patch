import sys,struct,csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
from castaway.quickdat import common_tables
iso=Iso9660(project_path(root,'original_iso'))
path=root/'translation'/'text_master.tsv'
with path.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f,delimiter='\t');fields=r.fieldnames;rows=list(r)
lookup={(r['resource_id'],int(r['string_index'])):r for r in rows}
for key in ('category','context_key','context_field'):
 if key not in fields:fields.append(key)
for r in rows:r.setdefault('category','');r.setdefault('context_key','');r.setdefault('context_field','')
reports=[]
for name,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/quickdat.arc')):
 if name=='world':continue
 bias=struct.unpack_from('<I',p,8)[0];count=sum(r['resource_id']==name for r in rows)
 tables=common_tables(p)
 for table in tables:
  reports.append({'resource':name,'table':table['name'],'rows':table['rows'],'stride':table['stride']})
  for i,key in enumerate(table['keys']):
   for field in range(0,table['stride'],4):
    value=struct.unpack_from('<I',table['data'],i*table['stride']+field)[0]
    if value<bias or value>=bias+count*4 or (value-bias)%4:continue
    row=lookup[(name,(value-bias)//4)]
    if row['category']:continue
    row.update(category=table['name'],context_key=key,context_field=str(field))
with path.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fields,delimiter='\t');w.writeheader();w.writerows(rows)
out=root/'logs'/'STEP_012';(out/'common_table_inventory.json').write_text(json.dumps(reports,indent=2),encoding='utf-8')
print('Rows with structural context:',sum(bool(r['category']) for r in rows))
for r in rows:
 if r['id']=='TXT_urbzui_01203':print(json.dumps(r,ensure_ascii=True))

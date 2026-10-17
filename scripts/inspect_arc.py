import sys,csv,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
rows=[];report=[]
for name in iso.files:
 if not name.endswith('.arc'):continue
 try:
  entries=read_arc(iso.read(name))
  report.append({'path':name,'status':'PASS','entries':len(entries)})
  for n,o,p,k in entries:rows.append([name,n,o,len(p),hex(k),p[:64].hex()])
 except Exception as e:report.append({'path':name,'status':'FAIL','error':str(e)})
out=root/'logs'/'STEP_009_inventory'
with (out/'arc_entries.tsv').open('w',encoding='utf-8',newline='') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['archive','name','offset','size','key','header_hex']);w.writerows(rows)
(out/'arc_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps({'entries':len(rows),'archives':report},indent=2))

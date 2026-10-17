import csv,json,re,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1];master=root/'translation'/'text_master.tsv'
with master.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f,delimiter='\t');fields=r.fieldnames;rows=list(r)
lookup={r['context_key']:r for r in rows if r['resource_id']=='urbzui'}
log=[]
for file in sorted((root/'translation'/'batches').glob('*_keys.json')):
 data=json.loads(file.read_text(encoding='utf-8-sig'))
 for key,text in data.items():
  if key not in lookup:raise ValueError('Unknown context key: '+key)
  row=lookup[key];source=row['source_text']
  if re.findall(r'<[^>]+>|%[-+0-9.]*[sdif]',source)!=re.findall(r'<[^>]+>|%[-+0-9.]*[sdif]',text):raise ValueError('Token mismatch: '+key)
  row['ko_current']=text;row['status']='DRAFT'
  log.append({'id':row['id'],'key':key,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'batch':file.name})
with master.open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fields,delimiter='\t');w.writeheader();w.writerows(rows)
(root/'logs'/'STEP_012'/'translation_batches.json').write_text(json.dumps(log,indent=2),encoding='utf-8')
print('Context-specific draft translations:',len(log));print('Total draft rows:',sum(bool(r['ko_current']) for r in rows))

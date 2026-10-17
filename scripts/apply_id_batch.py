import argparse,csv,json,hashlib,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('batch',type=Path);a=p.parse_args()
master=root/'translation/text_master.tsv'
with master.open(encoding='utf-8-sig',newline='') as f:r=csv.DictReader(f,delimiter='\t');fields=r.fieldnames;rows=list(r)
lookup={r['id']:r for r in rows}
entries=json.loads(a.batch.read_text(encoding='utf-8-sig'))
for item in entries:
 row=lookup[item['id']]
 if hashlib.sha256(row['source_text'].encode()).hexdigest()!=item['source_sha256']:raise ValueError('Source changed: '+item['id'])
 if row['ko_current'] and row['ko_current']!=item['ko']:raise ValueError('Existing translation differs: '+item['id'])
 token=r'<[^>]+>|%[-+0-9.]*[sdif]|\{[^}]+\}|\$[A-Za-z_]+(?::[0-9]+)?'
 if re.findall(token,row['source_text'])!=re.findall(token,item['ko']):raise ValueError('Token mismatch: '+item['id'])
for item in entries:
 row=lookup[item['id']];row['ko_current']=item['ko'];row['status']='DRAFT';note='batch:'+a.batch.name
 if note not in row['notes']:row['notes']=(row['notes']+'; '+note).strip('; ')
with master.open('w',encoding='utf-8-sig',newline='') as f:w=csv.DictWriter(f,fields,delimiter='\t');w.writeheader();w.writerows(rows)
print('Batch rows:',len(entries),'Total translated:',sum(bool(r['ko_current']) for r in rows))

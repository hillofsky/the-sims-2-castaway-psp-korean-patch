import csv,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
glossary=json.loads((root/'translation'/'glossary_ko.json').read_text(encoding='utf-8-sig'))
path=root/'translation'/'text_master.tsv'
with path.open(encoding='utf-8-sig',newline='') as f:
 reader=csv.DictReader(f,delimiter='\t');fields=reader.fieldnames;rows=list(reader)
changed=0
for row in rows:
 if row['source_text'] in glossary and not row['ko_current']:
  row['ko_current']=glossary[row['source_text']];row['status']='DRAFT';changed+=1
with path.open('w',encoding='utf-8',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields,delimiter='\t');writer.writeheader();writer.writerows(rows)
print('Draft translations applied:',changed)

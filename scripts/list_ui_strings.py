import csv
from pathlib import Path
p=Path(r'D:\심즈2캐스트어웨이\translation\text_master.tsv')
with p.open(encoding='utf-8-sig',newline='') as f:
 rows=list(csv.DictReader(f,delimiter='\t'))
for r in rows:
 if r['resource_id']=='urbzui' and len(r['source_text'])<48 and r['source_text'] and not r['source_text'].startswith(('TEMP','Boy','Girl','Male','Female')):
  print(r['id'],repr(r['source_text']))

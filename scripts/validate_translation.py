import csv,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
with (root/'translation'/'text_master.tsv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
issues=[];seen=set();draft=0
for r in rows:
 if r['id'] in seen:issues.append({'id':r['id'],'issue':'DUPLICATE_ID'})
 seen.add(r['id'])
 if not r['ko_current']:continue
 draft+=1
 source_tokens=re.findall(r'<[^>]+>|%[-+0-9.]*[sdif]|\{[^}]+\}|\$[A-Za-z_]+(?::[0-9]+)?',r['source_text'])
 target_tokens=re.findall(r'<[^>]+>|%[-+0-9.]*[sdif]|\{[^}]+\}|\$[A-Za-z_]+(?::[0-9]+)?',r['ko_current'])
 if source_tokens!=target_tokens:issues.append({'id':r['id'],'issue':'TOKEN_MISMATCH'})
 if len(r['ko_current'].encode(r['encoding']))>int(r['max_bytes']):issues.append({'id':r['id'],'issue':'EXCEEDS_EXISTING_ALLOCATION'})
report={'rows':len(rows),'draft_translated':draft,'untranslated':len(rows)-draft,'issues':issues,'runtime':'NOT_TESTED','note':'Existing allocation overflow is informational: variable-length pools are rebuilt. Runtime QA tracked separately.'}
(root/'logs'/'STEP_009_inventory'/'translation_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='issues'},ensure_ascii=True));print('Issue count:',len(issues))

fatal=[i for i in issues if i['issue']!='EXCEEDS_EXISTING_ALLOCATION']
raise SystemExit(1 if fatal else 0)

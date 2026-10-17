import sys, csv, re, json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.big import read_big
from castaway.refpack import decompress
iso = Iso9660(project_path(root,'original_iso'))
out = root/'logs'/'STEP_009_inventory'
rows, strings = [], []
def walk(data,path,depth=0):
    for name,off,payload in read_big(data):
        full = path+'::'+name
        rows.append([full,off,len(payload),payload[:16].hex()])
        if payload[:2] == b'\x10\xfb':
            payload = decompress(payload)
        if payload[:4] in (b'BIGF',b'BIG4') and depth < 8:
            walk(payload,full,depth+1)
        else:
            for m in re.finditer(rb'[\x20-\x7e]{8,}',payload):
                text=m.group().decode('ascii')
                if any(x in text.lower() for x in ('there is','load','new game','save','language','font','english','string')):
                    strings.append([full,m.start(),text])
for path in iso.files:
    if path.endswith('.viv'):
        walk(iso.read(path),path)
for file,head,records in [('apt_entries.tsv',['path','offset_in_parent','size','header_hex'],rows),('apt_string_candidates.tsv',['path','offset','text'],strings)]:
    with (out/file).open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(head);w.writerows(records)
print(json.dumps({'entries':len(rows),'candidates':len(strings)}))


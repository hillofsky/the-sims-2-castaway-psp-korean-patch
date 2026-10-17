"""Compare input images; write metadata only, never game payloads."""
import argparse, hashlib, json, csv, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from castaway.iso9660 import Iso9660, parse_sfo
from castaway.project import project_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = p.parse_args()
    out = args.root/'logs'/'STEP_009_inventory'
    out.mkdir(parents=True, exist_ok=True)
    results = {}
    for label, key in [('castaway', 'original_iso'), ('sims2_ko', 'reference_iso')]:
        path = project_path(args.root,key)
        iso = Iso9660(path)
        digest = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(8*1024*1024), b''):
                digest.update(block)
        with (out/(label+'_toc.tsv')).open('w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='\t')
            writer.writerow(['path','extent','size','header_hex'])
            for name, entry in sorted(iso.files.items()):
                with path.open('rb') as src:
                    src.seek(entry['extent']*2048)
                    header = src.read(min(64, entry['size']))
                writer.writerow([name, entry['extent'], entry['size'], header.hex()])
        results[label] = {'path':str(path),'size':path.stat().st_size,'sha256':digest.hexdigest(),'volume':iso.volume,'file_count':len(iso.files),'sfo':parse_sfo(iso.read('/PSP_GAME/PARAM.SFO'))}
    (out/'inputs.json').write_text(json.dumps(results,ensure_ascii=False,indent=2), encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()

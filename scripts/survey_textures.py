"""Extract source textures and numbered contact sheets for linguistic review."""
import argparse, csv, json, sys
from pathlib import Path
from PIL import Image, ImageDraw
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from castaway.iso9660 import Iso9660
from castaway.project import project_path
from castaway.arc import read_arc
from castaway.texture import decode_texture, image_header
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, default=root / 'work/texture_survey')
a = p.parse_args()
a.output.mkdir(parents=True, exist_ok=True)
iso = Iso9660(project_path(root, 'original_iso'))
records = []
for index, (name, offset, data, key) in enumerate(read_arc(iso.read('/PSP_GAME/USRDIR/data/textures.arc'))):
    target = a.output / ('texture_%04d.png' % index)
    record = {'index': index, 'name': name, 'key': hex(key), 'offset': offset, 'source_size': len(data), 'png': str(target.relative_to(root)), 'status': 'EXTRACTED_UNREVIEWED'}
    try:
        _, kind, _, w, h = image_header(data)
        record.update(width=w, height=h, format=hex(kind))
        decode_texture(data).save(target)
    except Exception as e:
        record.update(status='DECODE_FAILED', error=str(e))
    records.append(record)
(a.output / 'manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
for group, selected in [('large', [r for r in records if r.get('width', 0) >= 128 or r.get('height', 0) >= 128]), ('small', [r for r in records if r.get('width', 0) < 128 and r.get('height', 0) < 128])]:
    for page, start in enumerate(range(0, len(selected), 160)):
        subset = selected[start:start + 160]
        sheet = Image.new('RGB', (1600, 16 * 130), '#505050')
        draw = ImageDraw.Draw(sheet)
        for j, r in enumerate(subset):
            x, y = (j % 10) * 160, (j // 10) * 130
            if r['status'] == 'EXTRACTED_UNREVIEWED':
                img = Image.open(root / r['png']).convert('RGBA')
                img.thumbnail((156, 100))
                sheet.paste(img, (x + (156 - img.width) // 2, y), img)
            draw.text((x + 2, y + 102), str(r['index']) + ' ' + r['name'][:19], fill='white')
            draw.text((x + 2, y + 115), r['name'][19:43], fill='white')
            r['contact_sheet'] = 'sheet_%s_%02d.jpg' % (group, page)
        sheet.save(a.output / ('sheet_%s_%02d.jpg' % (group, page)), quality=92)
(a.output / 'manifest.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'textures': len(records), 'decoded': sum(r['status'] == 'EXTRACTED_UNREVIEWED' for r in records), 'failed_count': sum(r['status'] == 'DECODE_FAILED' for r in records), 'contact_sheets': len(list(a.output.glob('sheet_*.jpg')))}))

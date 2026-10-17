"""Build standalone PSP shell images, title metadata and save/load locale."""
import argparse, csv, hashlib, io, json, re, struct, sys
from pathlib import Path
from PIL import Image
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from castaway.iso9660 import Iso9660
from castaway.project import project_path
from castaway.locale import parse_locale, rebuild_locale
from castaway.texture import replace_bgr565_texture, decode_texture
p = argparse.ArgumentParser()
p.add_argument('--build-id', required=True)
a = p.parse_args()
iso = Iso9660(project_path(root, 'original_iso'))
folder = root / 'build' / ('supplemental_' + a.build_id)
folder.mkdir(exist_ok=True)
log = root / 'logs' / a.build_id
log.mkdir(exist_ok=True)
outputs = {}
reports = []
def save(path, data, name):
    target = folder / name
    target.write_bytes(data)
    outputs[path] = str(target.relative_to(root))
    reports.append({'path': path, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
path = '/PSP_GAME/USRDIR/data/locale/trc/eng_us.loc'
source = iso.read(path)
with (root / 'translation/supplemental_text.tsv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f, delimiter='\t'))
original = parse_locale(source)[2]
if len(original) != len(rows):
    raise ValueError('Supplemental locale count differs')
for i, r in enumerate(rows):
    if int(r['string_index']) != i or r['source_text'] != original[i]:
        raise ValueError('Supplemental source changed')
    token = r'<[^>]+>|%[0-9]*[sd]|%[0-9]+'
    if re.findall(token, original[i]) != re.findall(token, r['ko_current']):
        raise ValueError('Supplemental token mismatch: ' + r['id'])
save(path, rebuild_locale(source, [r['ko_current'] for r in rows]), 'eng_us.loc')
source = bytearray(iso.read('/PSP_GAME/PARAM.SFO'))
keys, values, count = struct.unpack_from('<III', source, 8)
for i in range(count):
    entry = 20 + i * 16
    key_offset, kind, length, capacity, offset = struct.unpack_from('<HHIII', source, entry)
    end = source.index(0, keys + key_offset)
    if source[keys + key_offset:end] == b'TITLE':
        title = '심즈 2: 캐스트어웨이'.encode('utf-8') + b'\0'
        if kind != 0x0204 or len(title) > capacity:
            raise ValueError('PSP title cannot fit')
        source[values + offset:values + offset + capacity] = title + b'\0' * (capacity - len(title))
        struct.pack_into('<I', source, entry + 4, len(title))
        break
else:
    raise ValueError('PSP TITLE missing')
save('/PSP_GAME/PARAM.SFO', bytes(source), 'PARAM.SFO')
assets = json.loads((root / 'config/supplemental_images.json').read_text(encoding='utf-8'))
for item in assets:
    path = item['path']
    image = Image.open(root / item['asset'])
    if item['format'] == 'bgr565':
        data = replace_bgr565_texture(iso.read(path), image)
        decode_texture(data).save(log / 'localized_boot.png')
    else:
        original_image = Image.open(io.BytesIO(iso.read(path)))
        image = image.convert('RGBA').resize(original_image.size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        data = buffer.getvalue()
    save(path, data, path.rsplit('/', 1)[1])
(folder / 'manifest.json').write_text(json.dumps(outputs, indent=2), encoding='utf-8')
(log / 'supplemental_build.json').write_text(json.dumps({'rows': len(rows), 'files': reports, 'runtime': 'NOT_TESTED_USER_OWNS_QA'}, indent=2), encoding='utf-8')
print(json.dumps({'locale_rows': len(rows), 'files': len(outputs)}))

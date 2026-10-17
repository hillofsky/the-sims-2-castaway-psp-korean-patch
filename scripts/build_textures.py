"""Build selected localized raster assets with original texture dimensions and palettes."""
import argparse, hashlib, json, sys
from pathlib import Path
from PIL import Image
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc, rebuild_arc
from castaway.texture import replace_dxt3_texture, replace_indexed_texture, decode_texture, image_header
p = argparse.ArgumentParser()
p.add_argument('--build-id', required=True)
a = p.parse_args()
iso = Iso9660(project_path(root, 'original_iso'))
original = iso.read('/PSP_GAME/USRDIR/data/textures.arc')
sources = {n: data for n, _, data, _ in read_arc(original)}
assets = json.loads((root / 'config/texture_replacements.json').read_text(encoding='utf-8'))
out = root / 'logs' / a.build_id
out.mkdir(exist_ok=True)
changes = {}
reports = []
for item in assets:
    name = item['resource']
    if name in changes:
        raise ValueError('Duplicate texture replacement: ' + name)
    source = sources[name]
    asset = root / item['asset']
    kind = image_header(source)[1]
    encoder = replace_indexed_texture if kind in (0x5c, 0x5d) else replace_dxt3_texture
    replacement = encoder(source, Image.open(asset))
    if len(source) != len(replacement):
        raise ValueError('Texture resource size changed: ' + name)
    preview = 'localized_' + name + '.png'
    decode_texture(replacement).save(out / preview)
    changes[name] = replacement
    reports.append({'resource': name, 'asset': item['asset'], 'asset_sha256': hashlib.sha256(asset.read_bytes()).hexdigest(), 'size_preserved': len(source), 'preview': preview, 'runtime': 'NOT_TESTED_USER_OWNS_QA'})
rebuilt = rebuild_arc(original, changes)
(root / 'build' / ('textures_' + a.build_id + '_DRAFT.arc')).write_bytes(rebuilt)
report = {'textures': reports, 'count': len(reports), 'runtime': 'NOT_TESTED_USER_OWNS_QA'}
(out / 'texture_build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))

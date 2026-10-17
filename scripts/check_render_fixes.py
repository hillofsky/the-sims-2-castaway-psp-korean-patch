"""Independent alpha decoder and source-metric checks; never launches the game."""
import argparse
import io
import json
import struct
import sys
from pathlib import Path
from PIL import Image
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from castaway.arc import read_arc
from castaway.font import parse_font
from castaway.texture import image_header, decode_texture
p = argparse.ArgumentParser()
p.add_argument('--build-id', required=True)
a = p.parse_args()
textures = read_arc((root / 'build' / ('textures_' + a.build_id + '_DRAFT.arc')).read_bytes())
logo = next(e[2] for e in textures if e[0] == 'logo_sims_castaway_en')
offset, kind, length, width, height = image_header(logo)
source = Image.open(root / 'translation/images/logo_sims_castaway_ko_v1.png').convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
# Reconstruct a standard DDS and ask Pillow's independent decoder to read it.
buffer = io.BytesIO()
source.save(buffer, format='DDS', pixel_format='DXT5')
standard = bytearray()
raw = logo[offset + 16:offset + length]
for pos in range(0, len(raw), 16):
    block = raw[pos:pos + 16]
    standard.extend(block[8:16] + block[4:8] + block[:4])
header = bytearray(buffer.getvalue()[:128])
header[84:88] = b'DXT3'
decoded = Image.open(io.BytesIO(header + standard)).convert('RGBA')
zero_errors = sum(s[3] == 0 and d[3] != 0 for s, d in zip(source.getdata(), decoded.getdata()))
opaque_errors = sum(s[3] == 255 and d[3] != 255 for s, d in zip(source.getdata(), decoded.getdata()))
if zero_errors or opaque_errors:
    raise ValueError('Logo alpha regression: %d transparent, %d opaque pixels' % (zero_errors, opaque_errors))
fonts = {n: parse_font(data) for n, _, data, _ in read_arc((root / 'build' / ('fonts_' + a.build_id + '_EXPERIMENTAL.arc')).read_bytes()) if n != 'auxgraph'}
metrics = {}
for name, f in fonts.items():
    hangul = [g for c, g in zip(f['codes'], f['glyphs']) if 0xac00 <= c <= 0xd7a3]
    metrics[name] = {'max_height': max(g[3] for g in hangul), 'top_min': min(struct.unpack_from('<b', g, 10)[0] for g in hangul), 'bottom_max': max(struct.unpack_from('<b', g, 10)[0] + g[3] for g in hangul)}
    if metrics[name]['max_height'] > (9 if name == 'sc_main10' else 10 if name == 'sc_main11' else 11):
        raise ValueError('Korean glyph exceeds selected UI cap height')
title, glow = fonts['sc_title'], fonts['sc_title_glow']
for code in set(title['codes']) & set(glow['codes']):
    if not 0xac00 <= code <= 0xd7a3:
        continue
    x = title['glyphs'][title['codes'].index(code)]
    y = glow['glyphs'][glow['codes'].index(code)]
    if (x[2:4], x[9:11], x[14:16]) != (y[2:4], y[9:11], y[14:16]):
        raise ValueError('Title/glow metrics disagree')
report = {'logo_zero_alpha_errors': zero_errors, 'logo_opaque_alpha_errors': opaque_errors, 'font_metrics': metrics, 'title_glow_metrics_match': True, 'runtime': 'NOT_TESTED_USER_OWNS_QA'}
(root / 'logs' / a.build_id / 'render_fix_checks.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))

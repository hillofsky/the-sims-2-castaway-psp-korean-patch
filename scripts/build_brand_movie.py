"""Translate the EA brand-identification caption, preserving original PMF timing/audio."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / 'src'))
from castaway.iso9660 import Iso9660
from castaway.project import project_path
from castaway.pmf import replace_video_groups
p = argparse.ArgumentParser()
p.add_argument('--build-id', required=True)
a = p.parse_args()
ffmpeg = shutil.which('ffmpeg')
if not ffmpeg:
    raise RuntimeError('FFmpeg required')
folder = root / 'build' / ('supplemental_' + a.build_id)
log = root / 'logs' / a.build_id
work = root / 'work' / ('brand_movie_' + a.build_id)
work.mkdir(exist_ok=True)
path = '/PSP_GAME/USRDIR/movies/english_eabrand.pmf'
source = Iso9660(project_path(root, 'original_iso')).read(path)
(work / 'original.pmf').write_bytes(source)
shutil.copyfile(project_path(root, 'raster_font'), work / 'font.ttf')
caption = json.loads((root / 'translation/movie_captions.json').read_text(encoding='utf-8'))
(work / 'caption.txt').write_text(caption['ko'], encoding='utf-8')
for crf in (18, 22, 26, 30, 34, 38, 42, 46):
    avc = work / ('localized_%d.h264' % crf)
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', 'original.pmf',
               '-vf', 'scale=in_range=full:out_range=tv,format=yuv420p,drawbox=x=0:y=225:w=iw:h=30:color=black:t=fill,drawtext=fontfile=font.ttf:textfile=caption.txt:fontsize=9:fontcolor=white:x=(w-text_w)/2:y=231',
               '-frames:v', '123', '-r', '30000/1001', '-an', '-c:v', 'libx264', '-profile:v', 'main',
               '-level:v', '2.1', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-x264-params',
               'aud=1:repeat-headers=1:bframes=0:ref=1:keyint=250:scenecut=0',
               '-force_key_frames', 'expr:eq(n,0)+eq(n,59)+eq(n,111)',
               '-f', 'h264', '-y', str(avc)]
    result = subprocess.run(command, cwd=work, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    try:
        movie, groups = replace_video_groups(source, avc.read_bytes())
        break
    except ValueError as error:
        (log / ('brand_movie_crf%d.txt' % crf)).write_text(str(error), encoding='utf-8')
else:
    raise ValueError('Localized brand movie does not fit PMF packet groups')
(folder / 'english_eabrand.pmf').write_bytes(movie)
manifest_path = folder / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest[path] = str((folder / 'english_eabrand.pmf').relative_to(root))
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
report = {'crf': crf, 'frames': 123, 'size_preserved': len(movie), 'groups': groups,
          'caption': caption, 'runtime': 'NOT_TESTED_USER_OWNS_QA', 'command': command}
(log / 'brand_movie_build.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ('groups', 'command')}))

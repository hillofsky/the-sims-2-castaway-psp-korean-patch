"""Localize the title strip while retaining upper motion and original PMF packets."""
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
    raise RuntimeError('FFmpeg required for localized PSP icon movie')
folder = root / 'build' / ('supplemental_' + a.build_id)
folder.mkdir(exist_ok=True)
log = root / 'logs' / a.build_id
log.mkdir(exist_ok=True)
source = Iso9660(project_path(root, 'original_iso')).read('/PSP_GAME/ICON1.PMF')
work = root / 'work' / ('icon_movie_' + a.build_id)
work.mkdir(exist_ok=True)
original = work / 'original.pmf'
original.write_bytes(source)
asset = root / 'translation/images/psp_icon_ko_v1.png'
for crf in (24, 28, 32, 36, 40, 44, 48):
    avc = work / ('localized_%d.h264' % crf)
    command = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-i', str(original), '-i', str(asset),
               '-filter_complex', '[1:v]scale=480:272,crop=480:142:0:110[title];[0:v][title]overlay=0:110',
               '-frames:v', '180', '-r', '30000/1001', '-an', '-c:v', 'libx264', '-profile:v', 'main',
               '-level:v', '2.1', '-pix_fmt', 'yuv420p', '-crf', str(crf), '-x264-params',
               'aud=1:repeat-headers=1:bframes=0:ref=1:keyint=250:scenecut=0',
               '-force_key_frames', 'expr:eq(n,0)+eq(n,58)+eq(n,117)+eq(n,168)',
               '-f', 'h264', '-y', str(avc)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr)
    try:
        movie, groups = replace_video_groups(source, avc.read_bytes())
        break
    except ValueError as error:
        (log / ('icon_movie_crf%d.txt' % crf)).write_text(str(error), encoding='utf-8')
else:
    raise ValueError('Localized video does not fit original PMF packet groups')
(folder / 'ICON1.PMF').write_bytes(movie)
manifest_path = folder / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
manifest['/PSP_GAME/ICON1.PMF'] = str((folder / 'ICON1.PMF').relative_to(root))
manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
report = {'crf': crf, 'frames': 180, 'width': 480, 'height': 272, 'size_preserved': len(movie),
          'groups': groups, 'animation_note': 'Lower localized title strip is stationary; source upper motion and nonvideo packets retained.',
          'runtime': 'NOT_TESTED_USER_OWNS_QA', 'command': command}
(log / 'icon_movie_build.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k not in ('groups', 'command')}))

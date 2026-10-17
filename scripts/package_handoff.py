"""Portable source, translations, compact evidence and selected binary patch."""
import argparse,json,zipfile,datetime,hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--output',type=Path);p.add_argument('--build-id');a=p.parse_args()
a.build_id=a.build_id or json.loads((root/'config/project.json').read_text(encoding='utf-8-sig'))['latest_build_id']
output=a.output or root/'logs'/('CASTAWAY_'+a.build_id+'_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_RESULT.zip')
if output.exists():raise FileExistsError(output)
files=[]
for directory in ('src','scripts','config','translation','logs'):
 path=root/directory
 if path.exists():
  files.extend(f for f in path.rglob('*') if f.is_file() and f.suffix.lower() in ('.py','.ps1','.json','.md','.tsv','.png','.txt','.log') and (f.suffix.lower()!='.png' or directory!='logs') and '__pycache__' not in f.parts and (directory!='logs' or f.stat().st_size<2_000_000) and 'package' not in f.relative_to(root).parts)
for name in ('PROJECT_STATE.md','README_LOCALIZATION.md','CHATGPT_HANDOFF.md','HANDOFF_NEXT.md','FINAL_HANDOFF.md','run.ps1','.gitignore','requirements.txt'):
 f=root/name
 if f.exists():files.append(f)
patch=root/'build'/('CASTAWAY_'+a.build_id+'_EXPERIMENTAL.patch.zip')
if patch.exists():files.append(patch)
for f in (root/'runtime'/'instances').rglob('*.json'):
 if f.stat().st_size<100_000:files.append(f)
# Small curated real runtime evidence; avoid memory dumps and log floods.
evidence=root/'runtime/instances/castaway_STEP010_20261016_225639_622'
for name in ('wide_title_menu','wide_crew_ready','cas_customization','occupation','cas_done_sequence'):
 f=evidence/(name+'.png')
 if f.exists():files.append(f)
evidence_config=root/'config/runtime_evidence.json'
if evidence_config.exists():
 for entry in json.loads(evidence_config.read_text(encoding='utf-8')):
  f=(root/entry['path']).resolve()
  if root.resolve() not in f.parents:raise ValueError('Evidence outside project')
  if f.exists():files.append(f)
output.parent.mkdir(parents=True,exist_ok=True)
manifest=[]
with zipfile.ZipFile(output,'x',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for file in sorted(set(files)):
  data=file.read_bytes();name=file.relative_to(root).as_posix();z.writestr(name,data);manifest.append({'path':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 z.writestr('PACKAGE_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
with zipfile.ZipFile(output) as z:
 if z.testzip():raise ValueError('ZIP verification failed')
 required={'translation/text_master.tsv','translation/supplemental_text.tsv','translation/movie_captions.json','translation/ASSET_SCOPE_083.md','config/project.json','config/texture_replacements.json','config/supplemental_images.json','src/castaway/index.py','src/castaway/dataset.py','src/castaway/locale.py','src/castaway/pmf.py','src/castaway/texture.py','scripts/build_pipeline.py','scripts/build_supplemental.py','scripts/build_icon_movie.py','scripts/build_brand_movie.py','scripts/apply_binary_patch.py','PROJECT_STATE.md','HANDOFF_NEXT.md','run.ps1','PACKAGE_MANIFEST.json'}
 if patch.exists():required.add(patch.relative_to(root).as_posix())
 if required-set(z.namelist()):raise ValueError('Required package members missing: '+str(required-set(z.namelist())))
 for entry in manifest:
  if hashlib.sha256(z.read(entry['path'])).hexdigest()!=entry['sha256']:raise ValueError('Package hash mismatch: '+entry['path'])
print(str(output).encode('ascii','backslashreplace').decode());print('bytes',output.stat().st_size,'files',len(manifest))

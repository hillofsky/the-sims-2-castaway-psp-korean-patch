"""Build from canonical TSV; never apply editorial batches implicitly."""
import argparse, datetime, hashlib, json, platform, re, subprocess, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'src'))
from castaway.project import project_path, project_config

def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()

p=argparse.ArgumentParser()
p.add_argument('--build-id',required=True)
p.add_argument('--verify-patch',action='store_true')
a=p.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_]+',a.build_id):p.error('Invalid build ID')
log=root/'logs'/a.build_id
if log.exists():raise FileExistsError('Build ID already used; select a fresh ID')
for pattern in (f'*{a.build_id}*.iso',f'*{a.build_id}*.arc',f'*{a.build_id}*.ind',f'*{a.build_id}*.zip'):
 if list((root/'build').glob(pattern)):raise FileExistsError('Build artifacts already exist')
log.mkdir(parents=True)
report={'build_id':a.build_id,'started':datetime.datetime.now().astimezone().isoformat(),'status':'RUNNING','commands':[],'python':platform.python_version()}
try:
 cfg=project_config(root)
 original=project_path(root,'original_iso')
 if digest(original)!=cfg['original_sha256']:raise ValueError('Original ISO SHA256 mismatch')
 report['inputs']={k:digest(path) for k,path in {'iso':original,'translation':root/'translation/text_master.tsv','font':project_path(root,'raster_font')}.items()}
 commands=[['validate_translation.py']]+[[s,'--build-id',a.build_id] for s in ('verify_rebuild.py','build_fonts.py','build_textures.py','build_supplemental.py','build_icon_movie.py','build_brand_movie.py','build_dataset_clones.py','build_global_index.py','build_experimental_iso.py','create_delta.py')]
 if a.verify_patch:
  commands.append(['apply_binary_patch.py','--source',str(original),'--patch',str(root/'build'/f'CASTAWAY_{a.build_id}_EXPERIMENTAL.patch.zip'),'--output',str(root/'build'/f'CASTAWAY_{a.build_id}_PATCH_REPRODUCED.iso')])
 for command in commands:
  print('Running',command[0],flush=True)
  with (log/(command[0]+'.log')).open('w',encoding='utf-8') as stream:
   result=subprocess.run([sys.executable,str(root/'scripts'/command[0]),*command[1:]],stdout=stream,stderr=subprocess.STDOUT,env=__import__('os').environ.copy()|{'PYTHONIOENCODING':'utf-8'})
  report['commands'].append({'args':command,'exit_code':result.returncode})
  if result.returncode:raise RuntimeError(command[0]+' failed; see its log')
 report['status']='BUILT_UNVERIFIED'
 import PIL
 report['pillow_version']=PIL.__version__
 report['source_sha256']={str(p.relative_to(root)):digest(p) for folder in ('src','scripts') for p in (root/folder).rglob('*.py')}
 cfg['latest_build_id']=a.build_id
 (root/'config/project.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
 report['target_sha256']=digest(root/'build'/f'CASTAWAY_{a.build_id}_KO_EXPERIMENTAL.iso')
except Exception as error:
 report['status']='FAILED';report['error']=str(error)
 raise
finally:
 report['finished']=datetime.datetime.now().astimezone().isoformat()
 (log/'pipeline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('source_sha256','commands')},ensure_ascii=True))

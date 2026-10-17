import sys,json,hashlib,csv,datetime,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso_patch import patch_iso
parser=argparse.ArgumentParser();parser.add_argument('--build-id',default='STEP018');parser.add_argument('--text-build-id');parser.add_argument('--font-build-id');parser.add_argument('--dataset-build-id');args=parser.parse_args();args.dataset_build_id=args.dataset_build_id or args.build_id;args.text_build_id=args.text_build_id or args.build_id;args.font_build_id=args.font_build_id or args.build_id
if not args.build_id.replace('_','').isalnum():raise ValueError('Invalid build ID')
original=project_path(root,'original_iso')
output=root/'build'/('CASTAWAY_'+args.build_id+'_KO_EXPERIMENTAL.iso')
replacements={'/PSP_GAME/USRDIR/data/quickdat.arc':(root/'build'/('quickdat_'+args.text_build_id+'_DRAFT.arc')).read_bytes(),'/PSP_GAME/USRDIR/data/fonts.arc':(root/'build'/('fonts_'+args.font_build_id+'_EXPERIMENTAL.arc')).read_bytes()}
replacements['/PSP_GAME/USRDIR/data/datasets.arc']=(root/'build'/('datasets_'+args.dataset_build_id+'_DRAFT.arc')).read_bytes()
replacements['/PSP_GAME/USRDIR/data/index.ind']=(root/'build'/('index_'+args.build_id+'.ind')).read_bytes()
replacements['/PSP_GAME/USRDIR/data/textures.arc']=(root/'build'/('textures_'+args.build_id+'_DRAFT.arc')).read_bytes()
supplemental=json.loads((root/'build'/('supplemental_'+args.build_id)/'manifest.json').read_text(encoding='utf-8'))
for path,file in supplemental.items():
 if path in replacements:raise ValueError('Duplicate ISO replacement')
 replacements[path]=(root/file).read_bytes()
manifest=patch_iso(original,output,replacements)
digest=hashlib.sha256()
with output.open('rb') as f:
 for chunk in iter(lambda:f.read(8*1024*1024),b''):digest.update(chunk)
report={'build_id':args.build_id+'_KO_EXPERIMENTAL','status':'BUILT_UNVERIFIED','runtime':'NOT_VERIFIED','output':str(output),'sha256':digest.hexdigest(),'files':manifest}
(root/'logs'/args.build_id).mkdir(exist_ok=True);(root/'logs'/args.build_id/'build_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=True,indent=2))




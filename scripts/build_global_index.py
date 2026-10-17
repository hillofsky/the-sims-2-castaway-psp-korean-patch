import sys,json,hashlib,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.index import update_index
parser=argparse.ArgumentParser();parser.add_argument('--build-id',default='STEP020');parser.add_argument('--font-build-id',default=None);parser.add_argument('--text-build-id');parser.add_argument('--dataset-build-id');args=parser.parse_args();args.font_build_id=args.font_build_id or args.build_id;args.text_build_id=args.text_build_id or args.build_id;args.dataset_build_id=args.dataset_build_id or args.build_id
iso=Iso9660(project_path(root,'original_iso'))
archives={}
for category,filename,built in [('Datasets','datasets.arc','datasets_'+args.dataset_build_id+'_DRAFT.arc'),('Fonts','fonts.arc','fonts_'+args.font_build_id+'_EXPERIMENTAL.arc'),('QuickDatas','quickdat.arc','quickdat_'+args.text_build_id+'_DRAFT.arc')]:
 archives[category]=(iso.read('/PSP_GAME/USRDIR/data/'+filename),(root/'build'/built).read_bytes())
original=iso.read('/PSP_GAME/USRDIR/data/index.ind')
archives['Textures']=(iso.read('/PSP_GAME/USRDIR/data/textures.arc'),(root/'build'/('textures_'+args.build_id+'_DRAFT.arc')).read_bytes())
nochange,_=update_index(original,{n:(old,old) for n,(old,new) in archives.items()});assert nochange==original
rebuilt,report=update_index(original,archives)
(root/'build'/('index_'+args.build_id+'.ind')).write_bytes(rebuilt)
out=root/'logs'/args.build_id;out.mkdir(exist_ok=True);(out/'global_index.json').write_text(json.dumps({'categories':report,'size':len(rebuilt),'sha256':hashlib.sha256(rebuilt).hexdigest()},indent=2),encoding='utf-8');print(json.dumps(report,indent=2))


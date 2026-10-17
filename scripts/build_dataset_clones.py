import sys,json,hashlib,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc,rebuild_arc
from castaway.dataset import parse_dataset,rebuild_dataset
parser=argparse.ArgumentParser();parser.add_argument('--build-id',default='STEP018');parser.add_argument('--text-build-id');args=parser.parse_args();args.text_build_id=args.text_build_id or args.build_id
iso=Iso9660(project_path(root,'original_iso'))
original=iso.read('/PSP_GAME/USRDIR/data/datasets.arc');quick=iso.read('/PSP_GAME/USRDIR/data/quickdat.arc');newquick=(root/'build'/('quickdat_'+args.text_build_id+'_DRAFT.arc')).read_bytes()
oldmap={key:(name,p) for name,o,p,key in read_arc(quick)};newmap={key:(name,p) for name,o,p,key in read_arc(newquick)}
texture_original=iso.read('/PSP_GAME/USRDIR/data/textures.arc')
texture_new=(root/'build'/('textures_'+args.build_id+'_DRAFT.arc')).read_bytes()
oldtextures={key:(name,p) for name,o,p,key in read_arc(texture_original)}
newtextures={key:(name,p) for name,o,p,key in read_arc(texture_new)}
changes={};reports=[];passes=0;unsupported=[]
for name,offset,payload,key in read_arc(original):
 try:
  _,_,entries=parse_dataset(payload);assert rebuild_dataset(payload,{})==payload;passes+=1
 except ValueError as err:unsupported.append({'name':name,'reason':str(err)});continue
 replacements={}
 for e in entries:
  if e['kind']=='QuickDatas' and e['key'] in oldmap:
   qname,expected=oldmap[e['key']];actual=payload[e['offset']:e['offset']+e['size']]
   if actual!=expected:raise ValueError('Known quickdat clone differs: '+name+'/'+qname)
   if newmap[e['key']][1]!=expected:
    replacements[e['index']]=newmap[e['key']][1];reports.append({'dataset':name,'asset_index':e['index'],'quickdat':qname,'old_size':len(expected),'new_size':len(replacements[e['index']])})
 for e in entries:
  if e['kind']=='Textures' and e['key'] in oldtextures:
   tname,expected=oldtextures[e['key']]
   replacement=newtextures[e['key']][1]
   if replacement!=expected:
    actual=payload[e['offset']:e['offset']+e['size']]
    if actual!=expected:raise ValueError('Known texture clone differs: '+name+'/'+tname)
    replacements[e['index']]=replacement;reports.append({'dataset':name,'asset_index':e['index'],'texture':tname,'old_size':len(expected),'new_size':len(replacement)})
 if replacements:changes[name]=rebuild_dataset(payload,replacements)
rebuilt=rebuild_arc(original,changes)
(root/'build'/('datasets_'+args.build_id+'_DRAFT.arc')).write_bytes(rebuilt)
out=root/'logs'/args.build_id;out.mkdir(exist_ok=True)
report={'dataset_roundtrips':passes,'unsupported':unsupported,'changes':reports,'size':len(rebuilt),'sha256':hashlib.sha256(rebuilt).hexdigest(),'runtime':'NOT_VERIFIED'}
(out/'dataset_build.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

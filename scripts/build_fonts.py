import sys,csv,json,hashlib,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc,rebuild_arc
from castaway.font import extend_font,parse_font
parser=argparse.ArgumentParser();parser.add_argument('--build-id',default='STEP015');args=parser.parse_args()
if not args.build_id.replace('_','').isalnum():raise ValueError('Invalid build ID')
iso=Iso9660(project_path(root,'original_iso'))
original=iso.read('/PSP_GAME/USRDIR/data/fonts.arc')
with (root/'translation'/'text_master.tsv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f,delimiter='\t'))
with (root/'translation/supplemental_text.tsv').open(encoding='utf-8-sig',newline='') as f:supplemental=list(csv.DictReader(f,delimiter='\t'))
chars=sorted({c for r in rows+supplemental for c in r['ko_current'] if ord(c)>127})
output=root/'logs'/args.build_id;output.mkdir(exist_ok=True)
replacements={};report=[]
for name,offset,payload,key in read_arc(original):
 if name=='auxgraph':continue
 # Korean ink must fit the original cap-height UI boxes. Keep title and glow
 # at the same raster size/advance so their overlays coincide.
 size=9 if name=='sc_main10' else 10 if name=='sc_main11' else 11
 new,atlas=extend_font(payload,chars,project_path(root,'raster_font'),size)
 replacements[name]=new
 if atlas is not None:atlas.resize((atlas.width*2,atlas.height*2)).save(output/(name+'_hangul.png'))
 before,after=parse_font(payload),parse_font(new)
 report.append({'name':name,'old_count':before['count'],'new_count':after['count'],'width':after['width'],'height':after['height'],'delta':len(new)-len(payload),'all_required_glyphs':set(map(ord,chars))<=set(after['codes']),'packing':atlas.info.get('packing',{}) if atlas is not None else {'mode':'unchanged'},'original_width':before['width'],'original_height':before['height'],'grid_capacity_at_512':(512//(size+2))*((512-before['height']-1)//(size+2)),'grid_remaining_at_512':(512//(size+2))*((512-before['height']-1)//(size+2))-(after['count']-before['count'])})
rebuilt=rebuild_arc(original,replacements);(root/'build'/('fonts_'+args.build_id+'_EXPERIMENTAL.arc')).write_bytes(rebuilt)
(output/'font_build.json').write_text(json.dumps({'required_characters':len(chars),'fonts':report,'original_size':len(original),'new_size':len(rebuilt),'sha256':hashlib.sha256(rebuilt).hexdigest(),'runtime':'NOT_TESTED','visual_style_note':'New glyphs rasterized from local Malgun; original glyph pixels preserved; glow styling not recreated.'},indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))


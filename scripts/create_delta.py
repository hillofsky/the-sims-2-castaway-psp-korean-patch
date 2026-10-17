import sys,json,argparse
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.delta import create_patch
parser=argparse.ArgumentParser();parser.add_argument('--build-id',default='STEP020');args=parser.parse_args()
report=create_patch(project_path(root,'original_iso'),root/'build'/('CASTAWAY_'+args.build_id+'_KO_EXPERIMENTAL.iso'),root/'build'/('CASTAWAY_'+args.build_id+'_EXPERIMENTAL.patch.zip'))
(root/'logs'/args.build_id/'delta_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report,indent=2))

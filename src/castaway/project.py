"""Small project configuration shared by command-line entry scripts."""
import json
from pathlib import Path

def project_config(root):
    return json.loads((Path(root)/'config'/'project.json').read_text(encoding='utf-8-sig'))

def project_path(root,key):
    value=Path(project_config(root)[key])
    return value if value.is_absolute() else Path(root)/value

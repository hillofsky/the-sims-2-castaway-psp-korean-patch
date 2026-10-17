"""Append relocated files to an ISO copy; update both-endian directory fields."""
import struct,shutil,hashlib
from pathlib import Path
from .iso9660 import Iso9660

def patch_iso(original,output,replacements):
    original,output=Path(original),Path(output)
    if original.resolve()==output.resolve():raise ValueError('Cannot overwrite original')
    if output.exists():raise FileExistsError(output)
    source=Iso9660(original)
    # Only primary ISO9660 supported; reject supplementary filesystems to avoid stale mirrored metadata.
    descriptors=[]
    with original.open('rb') as f:
        for sector in range(16,32):
            f.seek(sector*2048);d=f.read(2048)
            if d[1:6]!=b'CD001':raise ValueError('Invalid volume descriptor')
            descriptors.append((sector,d[0]))
            if d[0]==255:break
    if any(t not in (0,1,255) for _,t in descriptors):raise ValueError('Unsupported supplementary ISO descriptor')
    shutil.copyfile(original,output);manifest=[]
    with output.open('r+b') as f:
        f.seek(0,2)
        for path,data in sorted(replacements.items()):
            old=source.files[path]
            padding=(-f.tell())%2048;f.write(b'\x00'*padding)
            extent=f.tell()//2048;f.write(data);end=f.tell()
            f.seek(old['record_offset']+2);f.write(struct.pack('<I',extent)+struct.pack('>I',extent))
            f.seek(old['record_offset']+10);f.write(struct.pack('<I',len(data))+struct.pack('>I',len(data)))
            f.seek(end)
            manifest.append({'path':path,'old_extent':old['extent'],'extent':extent,'size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        f.write(b'\x00'*((-f.tell())%2048));sectors=f.tell()//2048
        for sector,kind in descriptors:
            if kind==1:
                f.seek(sector*2048+80);f.write(struct.pack('<I',sectors)+struct.pack('>I',sectors))
    rebuilt=Iso9660(output)
    for path,data in replacements.items():
        if rebuilt.read(path)!=data:raise ValueError('ISO re-extraction mismatch: '+path)
    for path,entry in source.files.items():
        if path not in replacements and rebuilt.files[path]!=entry:raise ValueError('Unintended directory mutation')
    return manifest

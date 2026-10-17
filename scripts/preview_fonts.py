import sys,struct
from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
root=Path(r'D:\심즈2캐스트어웨이');sys.path.insert(0,str(root/'src'))
from castaway.project import project_path
from castaway.iso9660 import Iso9660
from castaway.arc import read_arc
iso=Iso9660(project_path(root,'original_iso'))
for n,o,p,k in read_arc(iso.read('/PSP_GAME/USRDIR/data/fonts.arc')):
 start=p.find(b'FntM');d=p[start:];bdata=struct.unpack_from('<I',d,28)[0];w,h=struct.unpack_from('<HH',d,bdata+4);raw=d[bdata+16:bdata+16+(w*h+1)//2]
 pixels=bytes(v for b in raw for v in ((b&15)*17,(b>>4)*17))[:w*h]
 img=Image.frombytes('L',(w,h),pixels);img.resize((w*3,h*3)).save(root/'logs'/'STEP_011'/(n+'_linear.png'))
 print(n,w,h,'imagebytes',len(raw))

"""Draw a diagnostic text sheet with glyphs decoded from the built game font."""
import sys,csv,struct,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.arc import read_arc
from castaway.font import parse_font
arc=(root/'build'/'fonts_STEP015_EXPERIMENTAL.arc').read_bytes()
payload=next(e[2] for e in read_arc(arc) if e[0]=='sc_main13');f=parse_font(payload)
tail=f['data'][f['bmp']+16+f['pixel_size']:];alpha=[tail[48+i*4+3] for i in range(16)]
atlas=Image.frombytes('L',(f['width'],f['height']),bytes(alpha[p] for p in f['pixels']))
lookup={code:rec for code,rec in zip(f['codes'],f['glyphs'])}
canvas=Image.new('RGB',(960,520),'#17202d');draw=ImageDraw.Draw(canvas)
label=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',22)
draw.text((30,20),'폰트 구조 검증용 샘플 · 실제 게임 화면 아님',font=label,fill='#b7c4d8')
lines=['새 게임 시작','게임 계속하기','표류자 만들기','저장하고 종료','요리사  정비사  산림 관리원','소지품이 가득 차서 이 물건을 주울 수 없습니다.']
for i,text in enumerate(lines):
 image=Image.new('L',(900,24));x=0
 for char in text:
  rec=lookup.get(ord(char))
  if rec is None:raise ValueError('Missing glyph: '+char)
  _,w,h,gx,gy=struct.unpack_from('<HBBHH',rec)
  if w and h:image.paste(atlas.crop((gx,gy,gx+w,gy+h)),(x+struct.unpack_from('<b',rec,9)[0],rec[10]))
  x+=struct.unpack_from('<H',rec,14)[0] if f['stride']==16 else rec[8]
 scale=3 if i<5 else 2
 mask=image.crop((0,0,x,24)).resize((x*scale,24*scale),Image.Resampling.NEAREST)
 ink=Image.new('RGB',mask.size,'#f6f7f9');canvas.paste(ink,(30,70+i*70),mask)
canvas.save(root/'logs'/'STEP015'/'font_text_preview.png')
print('Diagnostic font sheet created')

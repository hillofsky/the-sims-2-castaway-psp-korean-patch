import sys,json,base64,time,argparse,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'src'))
from castaway.websocket import ws_connect,ws_send,ws_recv
p=argparse.ArgumentParser();p.add_argument('action',choices=['status','shot','press','resume','vram','diagnose','frame','findtext','pressframes','releaseall']);p.add_argument('--button',default='start');p.add_argument('--frames',type=int,default=4);p.add_argument('--settle',type=float,default=1.0);p.add_argument('--hold',type=float,default=0.15);p.add_argument('--name',default='screen');a=p.parse_args()
instance=Path((root/'logs'/'STEP_010'/'latest_instance.txt').read_text(encoding='utf-8-sig').strip())
info=json.loads((instance/'instance.json').read_text(encoding='utf-8-sig'))
if info['status'] not in ('STARTING','OS_IDENTITY_VERIFIED','ACTIVE'):raise ValueError('OS runtime identity not verified')
subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(root/'scripts'/'verify_runtime.ps1'),'-Instance',str(instance)],check=True,capture_output=True)
s=ws_connect('127.0.0.1',info['port'])
def rpc(event,**args):
 ws_send(s,json.dumps(dict(event=event,**args)))
 events=[]
 for _ in range(20000):
  msg=json.loads(ws_recv(s));events.append(msg.get('event'))
  if msg.get('event') in ('input.analog','input.buttons'):
   with (instance/'input_events.jsonl').open('a',encoding='utf-8') as trace:trace.write(json.dumps(msg)+'\n')
  if msg.get('event')==event:return msg
  if msg.get('event')=='error':raise ValueError(msg)
 raise ValueError('No matching response: '+str(events))
rpc('broadcast.config.get')
rpc('broadcast.config.set',disallowed={'logger':True})
status=rpc('game.status')
if (status.get('game') or {}).get('id')!=info['expected_game_id']:raise ValueError('Wrong game: '+str(status))
info['status']='ACTIVE';info['detected_game']=status['game'];(instance/'instance.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
if a.action=='diagnose':
 report={'game':status,'cpu':rpc('cpu.status'),'threads':rpc('hle.thread.list')};(instance/'diagnostic.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=True))
if a.action=='status':print(json.dumps(status));print(json.dumps(rpc('cpu.status')))
if a.action=='resume':print(json.dumps(rpc('cpu.resume')))
if a.action=='releaseall':
 rpc('input.buttons.send',buttons={key:False for key in ('left','right','up','down','cross','circle','triangle','square','start','select','ltrigger','rtrigger')});rpc('input.analog.send',x=0,y=0);print('Released owned input and centered analog')
if a.action=='pressframes':
 try:print(json.dumps(rpc('input.buttons.press',button=a.button,duration=max(1,min(a.frames,60)))))
 finally:rpc('input.buttons.send',buttons={a.button:False})
if a.action=='press':
 try:
  rpc('input.buttons.send',buttons={a.button:True});time.sleep(max(.02,min(a.hold,2.0)))
 finally:rpc('input.buttons.send',buttons={a.button:False})
 print('Pressed/released',a.button)
if a.action=='vram':
 data=base64.b64decode(rpc('memory.read',address=0x04000000,size=0x200000)['base64']);(instance/(a.name+'_04000000_00200000.bin')).write_bytes(data);print('VRAM nonzero bytes:',sum(bool(x) for x in data))
if a.action=='findtext':
 patterns={t:t.encode('utf-16le') for t in ('Start New Game','ASCII TEST NOW','Continue Game')}
 matches=[];overlap=b''
 for address in range(0x08800000,0x0a000000,0x100000):
  block=base64.b64decode(rpc('memory.read',address=address,size=0x100000)['base64']);data=overlap+block;base=address-len(overlap)
  for label,pattern in patterns.items():
   at=0
   while True:
    at=data.find(pattern,at)
    if at<0:break
    matches.append({'text':label,'address':hex(base+at),'context_hex':data[max(0,at-32):at+len(pattern)+32].hex()});at+=len(pattern)
  overlap=data[-128:]
 (instance/'text_hits.json').write_text(json.dumps(matches,indent=2),encoding='utf-8');print(json.dumps(matches))
if a.action=='frame':
 from PIL import Image
 import struct
 before=rpc('cpu.status');paused_here=not before['stepping']
 if paused_here:rpc('cpu.stepping')
 try:
  address,stride,width,height=0x04000000,512,480,272
  raw=base64.b64decode(rpc('memory.read',address=address,size=stride*height*2)['base64'])
  pixels=bytearray()
  for y in range(height):
   for x in range(width):
    v=struct.unpack_from('<H',raw,(y*stride+x)*2)[0];pixels.extend(((v&31)*255//31,((v>>5)&63)*255//63,((v>>11)&31)*255//31))
  Image.frombytes('RGB',(width,height),bytes(pixels)).save(instance/(a.name+'.png'))
  metadata={'run_id':info['run_id'],'game_id':info['expected_game_id'],'source':'software-rendered PSP VRAM','address':hex(address),'stride':stride,'width':width,'height':height,'format':'PSP RGB565, low bits red','png':a.name+'.png'}
  (instance/(a.name+'.json')).write_text(json.dumps(metadata,indent=2),encoding='utf-8');print(json.dumps(metadata))
 finally:
  if paused_here:rpc('cpu.resume')
if a.action=='shot':
 rpc('cpu.stepping')
 try:
  shot=rpc('gpu.buffer.screenshot');(instance/(a.name+'.png')).write_bytes(base64.b64decode(shot['uri'].split(',',1)[1]));print(str(instance/(a.name+'.png')).encode('ascii','backslashreplace').decode())
 finally:rpc('cpu.resume')
if a.action in ('press','pressframes'):time.sleep(max(0,min(a.settle,5)))
s.close()






















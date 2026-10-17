import sys, json, base64
sys.path.insert(0, "scripts")
from stage04_ws import ws_connect, ws_send, ws_recv
pat = bytes.fromhex("530041005600450020002500730000000000004f004b0021000000000043006100")
print("pat len", len(pat))
s = ws_connect("127.0.0.1", 8078)
s.settimeout(2.0)
try:
    while True:
        ws_recv(s, timeout=1)
except Exception:
    pass
ws_send(s, json.dumps({"event": "memory.read", "address": 0x09880000, "size": 0x10000}))
r = ws_recv(s, timeout=60)
d = json.loads(r)
raw = base64.b64decode(d["base64"])
print("got", len(raw))
i = raw.find(pat)
print("full-pat find:", hex(0x9880000 + i) if i >= 0 else -1)
sub = bytes.fromhex("4f004b002100000000")
j = raw.find(sub)
print("OKsub find:", hex(0x9880000 + j) if j >= 0 else -1)
print("bytes at 0x82380:", raw[0x2380:0x23A2].hex())
s.close()

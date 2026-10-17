import sys, json, base64
sys.path.insert(0, "scripts")
from stage04_ws import ws_connect, ws_send, ws_recv
pat = bytes.fromhex("53004100560045002000250073000000004f004b00210000000043006100")
print("pat", len(pat), pat.hex())
s = ws_connect("127.0.0.1", 8078)
s.settimeout(2.0)
try:
    while True:
        ws_recv(s, timeout=1)
except Exception:
    pass
ws_send(s, json.dumps({"event": "memory.read", "address": 0x09800000, "size": 0x100000}))
r = ws_recv(s, timeout=120)
d = json.loads(r)
if "base64" not in d:
    print("NO-DATA:", r[:200])
else:
    raw = base64.b64decode(d["base64"])
    print("got", len(raw))
    i = raw.find(pat)
    print("find:", hex(0x9800000 + i) if i >= 0 else -1)
    k = raw.find(bytes.fromhex("4f004b002100000000"))
    print("sub:", hex(0x9800000 + k) if k >= 0 else -1)
s.close()

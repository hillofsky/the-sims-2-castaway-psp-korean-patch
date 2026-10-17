"""Read emulated RAM region via WS memory.read, print hex + utf16le decode.
Usage: python stage04_memread.py <port> <addr_hex> <size_hex>
"""
import sys, json, base64
sys.path.insert(0, "scripts")
from stage04_ws import ws_connect, ws_send, ws_recv
port, addr, size = int(sys.argv[1]), int(sys.argv[2], 16), int(sys.argv[3], 16)
s = ws_connect("127.0.0.1", port)
s.settimeout(2.0)
try:
    while True:
        ws_recv(s, timeout=1)
except Exception:
    pass
ws_send(s, json.dumps({"event": "memory.read", "address": addr, "size": size}))
r = ws_recv(s, timeout=60)
d = json.loads(r)
raw = base64.b64decode(d["base64"])
print(f"addr={addr:#010x} size={len(raw)}")
for i in range(0, len(raw), 64):
    seg = raw[i:i+64]
    hx = " ".join(f"{b:02x}" for b in seg)
    print(f"{addr+i:#010x} {hx}")
txt = raw.decode("utf-16-le", errors="replace")
print("---- utf16le ----")
with open("logs/stage04/memctx_test_utf16.txt", "w", encoding="utf-8") as f:
    f.write(repr(txt))
print("wrote logs/stage04/memctx_test_utf16.txt, chars:", len(txt))
s.close()
